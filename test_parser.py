#!/usr/bin/env python3
"""Test script for job parser."""

from job_platform.parser.job_parser import parse_job_description

def main():
    # Test parsing functionality
    test_description = '''
    We are looking for a Senior Python Developer with 5+ years of experience.
    Skills required: Python, Django, React, AWS, Docker, Kubernetes.
    Salary: $120,000 - $150,000 per year.
    This is a remote position.

    Requirements:
    - 5+ years of Python development
    - Experience with React and Node.js
    - AWS cloud services
    - Docker and Kubernetes
    '''

    parsed = parse_job_description(test_description)
    print('Parsed Job:')
    print(f'Skills: {parsed.skills}')
    print(f'Experience Level: {parsed.experience_level}')
    print(f'Salary Range: {parsed.salary_min} - {parsed.salary_max}')
    print(f'Is Remote: {parsed.is_remote}')

    # Test edge cases
    print('\n--- Edge Case Tests ---')

    # Empty description
    empty_parsed = parse_job_description('')
    print(f'Empty description skills: {empty_parsed.skills}')

    # No matches
    no_match_parsed = parse_job_description('This job has no specific requirements.')
    print(f'No match skills: {no_match_parsed.skills}')
    print(f'No match experience: {no_match_parsed.experience_level}')

    print('\n✅ Parser test completed!')

if __name__ == "__main__":
    main()