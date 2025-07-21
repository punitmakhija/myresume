import os
import re
import mammoth
from bs4 import BeautifulSoup
import json

def extract_text_from_docx(docx_path):
    """Extract text and basic formatting from Word document"""
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value
            return html_content
    except Exception as e:
        print(f"Error reading Word document: {e}")
        return None

def parse_resume_content(html_content):
    """Parse the HTML content and extract resume sections"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    resume_data = {
        'name': '',
        'contact': {},
        'summary': '',
        'experience': [],
        'skills': [],
        'education': ''
    }
    
    text_content = soup.get_text()
    
    # Extract name (usually first line or prominent text)
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    if lines:
        resume_data['name'] = lines[0]
    
    # Extract contact info (phone, email)
    phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    
    phone_match = re.search(phone_pattern, text_content)
    email_match = re.search(email_pattern, text_content)
    
    if phone_match:
        resume_data['contact']['phone'] = phone_match.group(1)
    if email_match:
        resume_data['contact']['email'] = email_match.group(1)
    
    # Extract sections based on common headers
    sections = re.split(r'\n(?=(?:SUMMARY|EXPERIENCE|SKILLS|EDUCATION|Professional Experience))', text_content, flags=re.IGNORECASE)
    
    for section in sections:
        section_lower = section.lower()
        if 'summary' in section_lower:
            resume_data['summary'] = section.split('\n', 1)[1].strip() if '\n' in section else section.strip()
        elif 'experience' in section_lower or 'professional' in section_lower:
            # Parse experience entries
            exp_entries = parse_experience_section(section)
            resume_data['experience'] = exp_entries
        elif 'skill' in section_lower:
            resume_data['skills'] = parse_skills_section(section)
        elif 'education' in section_lower:
            resume_data['education'] = section.split('\n', 1)[1].strip() if '\n' in section else section.strip()
    
    return resume_data

def parse_experience_section(section):
    """Parse experience section into individual job entries"""
    experiences = []
    # Split by company names or job titles (this is a simplified approach)
    entries = re.split(r'\n(?=[A-Z][^,\n]*(?:,|\s+)[A-Z]{2}(?:\s|$))', section)
    
    for entry in entries[1:]:  # Skip the header
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        if len(lines) >= 2:
            exp = {
                'title': lines[0],
                'company': lines[1] if len(lines) > 1 else '',
                'duration': '',
                'responsibilities': []
            }
            
            # Extract duration (look for date patterns)
            date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})'
            for line in lines:
                if re.search(date_pattern, line):
                    exp['duration'] = line
                    break
            
            # Extract responsibilities (lines starting with bullet points or dashes)
            for line in lines[2:]:
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    exp['responsibilities'].append(line[1:].strip())
            
            experiences.append(exp)
    
    return experiences

def parse_skills_section(section):
    """Parse skills section"""
    skills = []
    lines = [line.strip() for line in section.split('\n') if line.strip()]
    
    for line in lines[1:]:  # Skip header
        if ':' in line:
            category, skill_list = line.split(':', 1)
            skills.append({
                'category': category.strip(),
                'skills': [skill.strip() for skill in skill_list.split(',')]
            })
        elif line.startswith('-') or line.startswith('•'):
            skills.append(line[1:].strip())
    
    return skills

def update_html_resume(resume_data, html_file_path):
    """Update the existing HTML resume with new data"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Update name
        if resume_data['name']:
            name_element = soup.find('h1', class_='name')
            if name_element:
                name_element.string = resume_data['name']
        
        # Update contact info
        if resume_data['contact'].get('phone'):
            phone_elements = soup.find_all(string=re.compile(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'))
            for element in phone_elements:
                element.replace_with(resume_data['contact']['phone'])
        
        if resume_data['contact'].get('email'):
            email_elements = soup.find_all(string=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'))
            for element in email_elements:
                element.replace_with(resume_data['contact']['email'])
        
        # Update summary
        if resume_data['summary']:
            summary_element = soup.find('div', class_='summary-card')
            if summary_element:
                p_tag = summary_element.find('p')
                if p_tag:
                    # Preserve the <strong> tag at the beginning if it exists
                    if p_tag.find('strong'):
                        strong_text = p_tag.find('strong').get_text()
                        p_tag.clear()
                        strong_tag = soup.new_tag('strong')
                        strong_tag.string = strong_text
                        p_tag.append(strong_tag)
                        p_tag.append(' ' + resume_data['summary'])
                    else:
                        p_tag.string = resume_data['summary']
        
        # Save updated HTML
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        
        print("✅ HTML resume updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating HTML resume: {e}")
        return False

def main():
    """Main function to sync Word document to HTML resume"""
    # Find Word document
    word_files = [f for f in os.listdir('.') if f.endswith(('.docx', '.doc'))]
    
    if not word_files:
        print("❌ No Word document found in repository")
        return
    
    # Use the first Word document found
    word_file = word_files[0]
    html_file = 'index.html'
    
    if not os.path.exists(html_file):
        print("❌ index.html not found in repository")
        return
    
    print(f"🔄 Syncing {word_file} to {html_file}...")
    
    # Extract content from Word document
    html_content = extract_text_from_docx(word_file)
    if not html_content:
        print("❌ Failed to extract content from Word document")
        return
    
    # Parse resume data
    resume_data = parse_resume_content(html_content)
    
    # Update HTML resume
    success = update_html_resume(resume_data, html_file)
    
    if success:
        print("🎉 Resume sync completed successfully!")
        
        # Log what was updated
        print("\n📋 Updated sections:")
        if resume_data['name']:
            print(f"   • Name: {resume_data['name']}")
        if resume_data['contact']:
            print(f"   • Contact: {resume_data['contact']}")
        if resume_data['summary']:
            print(f"   • Summary: {resume_data['summary'][:50]}...")
    else:
        print("❌ Resume sync failed!")

if __name__ == "__main__":
    main()
