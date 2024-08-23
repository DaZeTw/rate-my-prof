from bs4 import BeautifulSoup
import requests

def scrape_professor_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting the first name
    name_div = soup.find('div', class_='NameTitle__Name-dowf0z-0 cfjPUG')
    first_name = name_div.find('span').text if name_div else "First name not found"
    
    # Extracting the department
    department_element = soup.find('a', class_="TeacherDepartment__StyledDepartmentLink-fl79e8-0 iMmVHb",href=True)
    department = department_element.find('b').text if department_element else "Department not found"
    
    # Extracting the school name
    school_element = soup.find('a', href=True, text=True)  # Finding the next <a> tag with a href and text
    school = school_element.text if school_element else "School not found"

    reviews_elements = soup.find_all(class_='Comments__StyledComments-dzzyvm-0 gRjWel')
    reviews = [review.text for review in reviews_elements]

    # Extracting the overall quality rating
    quality_rating = soup.find('div', class_='RatingValue__Numerator-qw8sqy-2 liyUjw')
    overall_quality = quality_rating.text if quality_rating else "Overall quality not found"

    # Extracting the percentage of students who would take again
    take_again_element = soup.find_all('div', class_='FeedbackItem__FeedbackNumber-uof32n-1 kkESWs')[0]
    would_take_again = take_again_element.text if take_again_element else "N/A"

    # Extracting the level of difficulty
    difficulty_element = soup.find_all('div', class_='FeedbackItem__FeedbackNumber-uof32n-1 kkESWs')[1]
    level_of_difficulty = difficulty_element.text if difficulty_element else "N/A"

    # Print all the values
    print(f"Professor Name: {first_name}")
    print(f"Department: {department}")
    print(f"School: {school}")
    print(f"Overall Quality: {overall_quality}")
    print(f"Would Take Again: {would_take_again}")
    print(f"Level of Difficulty: {level_of_difficulty}")
    print("Reviews:")
    for i, review in enumerate(reviews, 1):
        print(f"{i}. {review}")
    
    return {
        'name': first_name,
        'department': department,
        'school': school,
        'overall_quality': overall_quality,
        'would_take_again': would_take_again,
        'level_of_difficulty': level_of_difficulty,
        'reviews': reviews
    }


