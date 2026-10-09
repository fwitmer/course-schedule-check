# Schedule Checker Team - Austin Edwards, John Schwenke, and Conner Trouy
# May 4th, 2023 / Updated Oct 2026
#
# Dependencies:
#   Course data is retrieved directly from Curric API: https://curric.uaa.alaska.edu/ajax/ajaxScheduleSearch.php

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from website.models import MajorRequirements, Subjects
import json
import urllib.request
import concurrent.futures
import pandas as pd
import re


def calendar(request):
    # queries database tables MajorRequirements and Subjects used to populate dropdown menus 
    degree_major_data = MajorRequirements.objects.values('degree', 'major').annotate(count=Count('index')).order_by('degree', 'major')
    subject_data = Subjects.objects.values('subject', 'subj').order_by('subject', 'subj')
    context = {
        'degree_major_data': degree_major_data,
        'subject_data': subject_data
    }
    return render(request, 'scheduler.html', context)


def fetch_schedule_json(url):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CourseScheduleChecker'}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list):
                return data
    except Exception as e:
        print(f"Error querying {url}: {e}")
    return []


def parse_time(time_str):
    """
    Convert a time string in 'hhmma' format (e.g., '1000am', '0100pm') to military time (24-hour) format.
    """
    if not time_str or not isinstance(time_str, str):
        return time_str
    time_str = time_str.strip()
    if len(time_str) == 6:
        try:
            hours = int(time_str[:2])
            minutes = int(time_str[2:4])
            meridian = time_str[4:].upper()
            if meridian == "PM" and hours != 12:
                hours += 12
            elif meridian == "AM" and hours == 12:
                hours = 0
            return f"{hours:02d}{minutes:02d}"
        except ValueError:
            return time_str
    return time_str


def get_major_requirements(request):
    # get term, majors, and subject from client
    selected_term = request.GET.get('term')
    selected_majors = request.GET.get('majors')    
    selected_subjects = request.GET.get('subjects')

    if not selected_term:
        return JsonResponse({'data': '[]'})

    # selected_subjects can be empty
    selected_subj = []
    if selected_subjects:
        for subject in selected_subjects.split(','):
            subject = subject.strip()
            if ' - ' in subject:
                abbreviation, _ = subject.split(' - ', 1)
                selected_subj.append(abbreviation.strip())
            elif subject:
                selected_subj.append(subject)

    # retrieve requirements for each selected major
    courses = set()
    if selected_majors:
        for degree_major in selected_majors.split(','):
            degree_major = degree_major.strip()
            if ' (' in degree_major and degree_major.endswith(')'):
                major, degree = degree_major.rsplit(' (', 1)
                degree = degree[:-1]
                for req in MajorRequirements.objects.filter(degree=degree.strip(), major=major.strip()):
                    if req.course:
                        courses.add(req.course.strip())

    # Remove courses included in the selected subjects
    courses = [c for c in courses if not any(c.startswith(subj + " ") for subj in selected_subj)]
    courses = sorted(courses)

    # create a dictionary of courses by subject
    courses_by_subject = {}
    for course in courses:
        parts = course.split()
        if len(parts) >= 2:
            courses_by_subject.setdefault(parts[0], []).append(parts[1])

    # create appropriate urls for Curric JSON API
    urls = []
    for subj, numbers in courses_by_subject.items():
        course_numbers = ",".join(num.replace(" ", "+") for num in numbers)
        url = f"https://curric.uaa.alaska.edu/ajax/ajaxScheduleSearch.php?term={selected_term}&subj={subj}&crse={course_numbers}"
        urls.append(url)
    for subj in selected_subj:
        url = f"https://curric.uaa.alaska.edu/ajax/ajaxScheduleSearch.php?term={selected_term}&subj={subj}"
        urls.append(url)

    if not urls:
        return JsonResponse({'data': '[]'})

    all_records = []
    thread_count = min(8, len(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(fetch_schedule_json, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            all_records.extend(future.result())

    if not all_records:
        return JsonResponse({'data': '[]'})

    clean_ws = lambda x: re.sub(r'\s{2,}', ' ', str(x).strip()) if x else ''

    rows = []
    for rec in all_records:
        bldg = clean_ws(rec.get('building', ''))
        room = clean_ws(rec.get('room', ''))

        # Delivery method: mark ONLINE if room is ONLINE or bldg is DIST
        if room == 'ONLINE' or bldg == 'DIST':
            del_mthd = 'ONLINE'
        else:
            del_mthd = 'FACE'

        rows.append({
            'CRN': clean_ws(rec.get('crn', '')),
            'Subj': clean_ws(rec.get('subj', '')),
            'Crs': clean_ws(rec.get('crs', '')),
            'Sec': clean_ws(rec.get('sec', '')),
            'Title': clean_ws(rec.get('title', '')),
            'Days': clean_ws(rec.get('days', '')),
            'STime': parse_time(rec.get('stime', '')),
            'ETime': parse_time(rec.get('etime', '')),
            'Bldg': bldg,
            'Room': room,
            'Instructor': clean_ws(rec.get('instructors', '')),
            'DelMthd': del_mthd,
        })

    class_data_df = pd.DataFrame(rows)
    class_data_df = class_data_df.drop_duplicates(subset=['CRN', 'Days', 'STime', 'ETime'])
    class_data_json = class_data_df.to_json(orient='records')
    return JsonResponse({'data': class_data_json})