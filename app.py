from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
import time
import os
import json

import os
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
CORS(app)

# Groq client - reads GROQ_API_KEY from environment
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --- COMPREHENSIVE NIGERIAN COURSE DATABASE ---
# ⚠️  YEARLY UPDATE CHECKLIST (update at the start of each admission season):
# 1. JAMB cutoff marks        → check jamb.gov.ng (announced March/April yearly)
# 2. Tuition fees             → check each university's official website
# 3. New universities         → add any newly accredited institutions
# 4. Course accreditation     → verify NUC accreditation at nuc.edu.ng
# 5. Post-UTME requirements   → check each school's official portal
# Last updated: 2024 admission session
COURSES = [
    # ========== ENGINEERING ==========
    {
        'id': 'cs', 'title': 'Computer Science', 'category': 'Engineering',
        'description': 'Build software, AI systems, and digital solutions powering the future.',
        'req_subjects': ['math', 'phys', 'comp'], 'req_interests': ['code', 'build', 'sci'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Junior Developer', 'Software Engineer', 'Tech Lead', 'CTO'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 260, 'catchment': ['Lagos', 'Ogun', 'Osun', 'Oyo', 'Ekiti', 'Ondo'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 230, 'catchment': ['Kaduna', 'Kano', 'Katsina', 'Zamfara'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 250, 'catchment': ['Oyo', 'Osun', 'Ogun'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Federal University of Technology, Akure (FUTA)', 'cutoff': 220, 'catchment': ['Ondo', 'Ekiti'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Covenant University', 'cutoff': 200, 'catchment': [], 'tuition': '₦1,200,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Yaba College of Technology (YABATECH)', 'cutoff': 180, 'catchment': ['Lagos'], 'tuition': '₦40,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
            {'name': 'Federal Polytechnic Ilaro', 'cutoff': 170, 'catchment': ['Ogun'], 'tuition': '₦35,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'elect_eng', 'title': 'Electrical/Electronics Engineering', 'category': 'Engineering',
        'description': 'Design power systems, circuits, and electronic devices that drive modern life.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['build', 'sci', 'code'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Graduate Engineer', 'Design Engineer', 'Project Manager', 'Chief Engineer'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 270, 'catchment': ['Lagos', 'Ogun'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 250, 'catchment': ['Enugu', 'Anambra', 'Ebonyi'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 260, 'catchment': ['Osun', 'Oyo', 'Ogun'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 240, 'catchment': ['Edo', 'Delta'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Auchi Polytechnic', 'cutoff': 160, 'catchment': ['Edo'], 'tuition': '₦35,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'mech_eng', 'title': 'Mechanical Engineering', 'category': 'Engineering',
        'description': 'Design machines, vehicles, and manufacturing systems that power industries.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['build', 'sci', 'money'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Graduate Engineer', 'Design Engineer', 'Plant Manager', 'Engineering Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 265, 'catchment': ['Lagos', 'Ogun'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 240, 'catchment': ['Kaduna', 'Kano'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Federal University of Technology, Minna', 'cutoff': 210, 'catchment': ['Niger', 'Kwara'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Kaduna Polytechnic', 'cutoff': 165, 'catchment': ['Kaduna'], 'tuition': '₦30,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'civil_eng', 'title': 'Civil Engineering', 'category': 'Engineering',
        'description': 'Build bridges, roads, buildings, and infrastructure that shape cities.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['build', 'sci', 'money'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Site Engineer', 'Structural Engineer', 'Project Manager', 'Construction Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 260, 'catchment': ['Lagos', 'Ogun'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 250, 'catchment': ['Oyo', 'Osun'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Federal University of Technology, Owerri (FUTO)', 'cutoff': 220, 'catchment': ['Imo', 'Abia'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Federal Polytechnic Nekede', 'cutoff': 160, 'catchment': ['Imo'], 'tuition': '₦30,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'chem_eng', 'title': 'Chemical Engineering', 'category': 'Engineering',
        'description': 'Transform raw materials into valuable products in oil, gas, and manufacturing.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['sci', 'build', 'money'],
        'compulsory_subjects': ['math', 'chem', 'phys'],
        'career_path': ['Process Engineer', 'Plant Engineer', 'Production Manager', 'Technical Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 270, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 260, 'catchment': ['Osun', 'Oyo'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 245, 'catchment': ['Kaduna', 'Kano'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'pet_eng', 'title': 'Petroleum Engineering', 'category': 'Engineering',
        'description': 'Explore, extract, and manage oil & gas resources powering the economy.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['build', 'money', 'sci'],
        'compulsory_subjects': ['math', 'phys', 'chem'],
        'career_path': ['Field Engineer', 'Drilling Supervisor', 'Reservoir Manager', 'Oil Executive'],
        'universities': [
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 250, 'catchment': ['Edo', 'Delta'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Federal University of Petroleum Resources (FUPRE)', 'cutoff': 230, 'catchment': ['Delta', 'Bayelsa', 'Rivers'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 260, 'catchment': ['Oyo', 'Osun'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Petroleum Training Institute (PTI)', 'cutoff': 160, 'catchment': [], 'tuition': '₦30,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'agric_eng', 'title': 'Agricultural Engineering', 'category': 'Engineering',
        'description': 'Design farm machinery and irrigation systems to boost food production.',
        'req_subjects': ['math', 'phys', 'agric'], 'req_interests': ['build', 'agric', 'sci'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Farm Equipment Engineer', 'Irrigation Specialist', 'Agri-Tech Manager', 'Director'],
        'universities': [
            {'name': 'Federal University of Agriculture, Abeokuta (FUNAAB)', 'cutoff': 200, 'catchment': ['Ogun', 'Lagos'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 210, 'catchment': ['Enugu', 'Anambra'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 200, 'catchment': ['Kaduna', 'Kano'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    # ========== HEALTH SCIENCES ==========
    {
        'id': 'med', 'title': 'Medicine & Surgery', 'category': 'Health',
        'description': 'The pinnacle of healthcare. Diagnose, treat, and save lives as a doctor.',
        'req_subjects': ['bio', 'chem', 'phys'], 'req_interests': ['care', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem', 'phys'],
        'career_path': ['House Officer', 'Resident Doctor', 'Consultant', 'Chief Medical Director'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 290, 'catchment': ['Oyo', 'Osun'], 'tuition': '₦60,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 285, 'catchment': ['Lagos', 'Ogun'], 'tuition': '₦55,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 270, 'catchment': ['Kaduna', 'Kano'], 'tuition': '₦50,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 275, 'catchment': ['Enugu', 'Anambra'], 'tuition': '₦55,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'Afe Babalola University', 'cutoff': 200, 'catchment': [], 'tuition': '₦2,500,000', 'duration': '6 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'pharmacy', 'title': 'Pharmacy', 'category': 'Health',
        'description': 'Discover, develop, and dispense medications that heal and protect.',
        'req_subjects': ['bio', 'chem', 'math'], 'req_interests': ['care', 'sci', 'money'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Intern Pharmacist', 'Clinical Pharmacist', 'Pharmacy Manager', 'Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 270, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 275, 'catchment': ['Oyo', 'Osun'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 260, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 260, 'catchment': ['Enugu', 'Anambra'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'nursing', 'title': 'Nursing Science', 'category': 'Health',
        'description': 'Provide compassionate patient care and support the healthcare system.',
        'req_subjects': ['bio', 'chem', 'eng'], 'req_interests': ['care', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Staff Nurse', 'Senior Nurse', 'Matron', 'Chief Nursing Officer'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 230, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 240, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 220, 'catchment': ['Osun'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 210, 'catchment': ['Edo', 'Delta'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'dentistry', 'title': 'Dentistry', 'category': 'Health',
        'description': 'Specialize in oral health, dental surgery, and beautiful smiles.',
        'req_subjects': ['bio', 'chem', 'phys'], 'req_interests': ['care', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem', 'phys'],
        'career_path': ['House Officer', 'Dental Surgeon', 'Consultant', 'Head of Department'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 280, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 285, 'catchment': ['Oyo'], 'tuition': '₦60,000', 'duration': '6 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 270, 'catchment': ['Osun'], 'tuition': '₦50,000', 'duration': '6 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'physio', 'title': 'Physiotherapy', 'category': 'Health',
        'description': 'Restore movement and function through physical therapy and rehabilitation.',
        'req_subjects': ['bio', 'chem', 'phys'], 'req_interests': ['care', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Intern', 'Physiotherapist', 'Senior Therapist', 'Head of Rehabilitation'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 250, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 255, 'catchment': ['Oyo'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 240, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'medlab', 'title': 'Medical Laboratory Science', 'category': 'Health',
        'description': 'Analyze samples and conduct tests critical for medical diagnoses.',
        'req_subjects': ['bio', 'chem', 'phys'], 'req_interests': ['sci', 'care', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Lab Scientist', 'Senior Scientist', 'Lab Manager', 'Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 230, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 220, 'catchment': ['Enugu'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 210, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    # ========== SCIENCES ==========
    {
        'id': 'biochem', 'title': 'Biochemistry', 'category': 'Sciences',
        'description': 'Study the chemistry of living organisms and biological processes.',
        'req_subjects': ['bio', 'chem', 'math'], 'req_interests': ['sci', 'care', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Lab Assistant', 'Research Scientist', 'Senior Researcher', 'Professor'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 220, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 230, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 210, 'catchment': ['Enugu'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'microbio', 'title': 'Microbiology', 'category': 'Sciences',
        'description': 'Study microorganisms and their applications in medicine and industry.',
        'req_subjects': ['bio', 'chem', 'math'], 'req_interests': ['sci', 'care', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Lab Technician', 'Microbiologist', 'Quality Control Manager', 'Research Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 215, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 225, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 200, 'catchment': ['Enugu'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'physics', 'title': 'Physics', 'category': 'Sciences',
        'description': 'Understand the fundamental laws governing the universe.',
        'req_subjects': ['math', 'phys', 'chem'], 'req_interests': ['sci', 'build', 'code'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Graduate Assistant', 'Research Scientist', 'Professor', 'Research Director'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 210, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 200, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 190, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'chemistry', 'title': 'Chemistry', 'category': 'Sciences',
        'description': 'Study matter, its properties, and how substances interact.',
        'req_subjects': ['chem', 'math', 'phys'], 'req_interests': ['sci', 'build', 'care'],
        'compulsory_subjects': ['chem', 'math'],
        'career_path': ['Lab Chemist', 'Quality Analyst', 'Research Chemist', 'Chief Scientist'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 205, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 195, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 190, 'catchment': ['Enugu'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'math', 'title': 'Mathematics', 'category': 'Sciences',
        'description': 'Master abstract reasoning and solve complex problems.',
        'req_subjects': ['math', 'phys', 'eng'], 'req_interests': ['code', 'sci', 'build'],
        'compulsory_subjects': ['math'],
        'career_path': ['Analyst', 'Data Scientist', 'Actuary', 'Professor'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 200, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 190, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 180, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== BUSINESS ==========
    {
        'id': 'acct', 'title': 'Accounting', 'category': 'Business',
        'description': 'The language of business. Manage finances and audit corporations.',
        'req_subjects': ['math', 'econ', 'eng'], 'req_interests': ['money', 'law', 'build'],
        'compulsory_subjects': ['math', 'econ'],
        'career_path': ['Audit Trainee', 'Chartered Accountant', 'Finance Manager', 'CFO'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 250, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Covenant University', 'cutoff': 200, 'catchment': [], 'tuition': '₦900,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 230, 'catchment': ['Edo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Yaba College of Technology (YABATECH)', 'cutoff': 170, 'catchment': ['Lagos'], 'tuition': '₦40,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
            {'name': 'Auchi Polytechnic', 'cutoff': 160, 'catchment': ['Edo'], 'tuition': '₦35,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
    {
        'id': 'banking', 'title': 'Banking & Finance', 'category': 'Business',
        'description': 'Master banking operations, investments, and financial markets.',
        'req_subjects': ['math', 'econ', 'eng'], 'req_interests': ['money', 'law', 'build'],
        'compulsory_subjects': ['math', 'econ'],
        'career_path': ['Bank Officer', 'Relationship Manager', 'Branch Manager', 'Executive Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 240, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 220, 'catchment': ['Edo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Covenant University', 'cutoff': 200, 'catchment': [], 'tuition': '₦900,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'busadmin', 'title': 'Business Administration', 'category': 'Business',
        'description': 'Learn to manage organizations and lead business operations.',
        'req_subjects': ['math', 'econ', 'eng'], 'req_interests': ['money', 'build', 'law'],
        'compulsory_subjects': ['math', 'econ'],
        'career_path': ['Management Trainee', 'Manager', 'Director', 'CEO'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 235, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 225, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 230, 'catchment': ['Oyo'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'econ', 'title': 'Economics', 'category': 'Business',
        'description': 'Analyze economic systems, markets, and policy impacts.',
        'req_subjects': ['math', 'econ', 'eng'], 'req_interests': ['money', 'sci', 'law'],
        'compulsory_subjects': ['math', 'econ'],
        'career_path': ['Research Analyst', 'Economist', 'Policy Advisor', 'Chief Economist'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 230, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 240, 'catchment': ['Oyo'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 220, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'marketing', 'title': 'Marketing', 'category': 'Business',
        'description': 'Master brand strategy, consumer behavior, and sales optimization.',
        'req_subjects': ['econ', 'eng', 'math'], 'req_interests': ['money', 'write', 'build'],
        'compulsory_subjects': ['econ', 'eng'],
        'career_path': ['Marketing Executive', 'Brand Manager', 'Marketing Director', 'CMO'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 220, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Benin (UNIBEN)', 'cutoff': 200, 'catchment': ['Edo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== ARTS & HUMANITIES ==========
    {
        'id': 'law', 'title': 'Law', 'category': 'Arts',
        'description': 'Uphold justice, interpret constitutions, and defend rights.',
        'req_subjects': ['lit', 'govt', 'eng'], 'req_interests': ['law', 'write', 'money'],
        'compulsory_subjects': ['lit', 'eng'],
        'career_path': ['Associate', 'Senior Counsel', 'Partner', 'SAN / Judge'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 270, 'catchment': ['Lagos', 'Ogun'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 275, 'catchment': ['Oyo', 'Osun'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 260, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 255, 'catchment': ['Enugu', 'Anambra'], 'tuition': '₦45,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Babcock University', 'cutoff': 200, 'catchment': [], 'tuition': '₦1,200,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'masscom', 'title': 'Mass Communication', 'category': 'Arts',
        'description': 'Master journalism, broadcasting, and public relations.',
        'req_subjects': ['eng', 'lit', 'govt'], 'req_interests': ['write', 'media', 'law'],
        'compulsory_subjects': ['eng'],
        'career_path': ['Reporter', 'Editor', 'News Anchor', 'Media Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 240, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 220, 'catchment': ['Enugu'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 210, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'english', 'title': 'English & Literary Studies', 'category': 'Arts',
        'description': 'Master language, literature, and creative expression.',
        'req_subjects': ['eng', 'lit', 'govt'], 'req_interests': ['write', 'teach', 'media'],
        'compulsory_subjects': ['eng', 'lit'],
        'career_path': ['Writer', 'Editor', 'Lecturer', 'Professor'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 210, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 200, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 190, 'catchment': ['Osun'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'theatre', 'title': 'Theatre Arts', 'category': 'Arts',
        'description': 'Master acting, directing, and theatrical production.',
        'req_subjects': ['eng', 'lit', 'govt'], 'req_interests': ['media', 'write', 'build'],
        'compulsory_subjects': ['eng', 'lit'],
        'career_path': ['Actor', 'Director', 'Producer', 'Studio Owner'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 200, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 190, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 180, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== SOCIAL SCIENCES ==========
    {
        'id': 'polsci', 'title': 'Political Science', 'category': 'Social Sciences',
        'description': 'Study governance, political systems, and international relations.',
        'req_subjects': ['govt', 'econ', 'eng'], 'req_interests': ['law', 'public', 'write'],
        'compulsory_subjects': ['govt', 'eng'],
        'career_path': ['Political Analyst', 'Policy Advisor', 'Diplomat', 'Politician'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 220, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 230, 'catchment': ['Oyo'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 200, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'sociology', 'title': 'Sociology', 'category': 'Social Sciences',
        'description': 'Study society, social behavior, and cultural patterns.',
        'req_subjects': ['govt', 'econ', 'eng'], 'req_interests': ['public', 'write', 'care'],
        'compulsory_subjects': ['govt', 'eng'],
        'career_path': ['Research Assistant', 'Social Worker', 'Policy Analyst', 'Professor'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 200, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 210, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'psych', 'title': 'Psychology', 'category': 'Social Sciences',
        'description': 'Understand the human mind, behavior, and mental processes.',
        'req_subjects': ['bio', 'eng', 'govt'], 'req_interests': ['care', 'sci', 'write'],
        'compulsory_subjects': ['eng'],
        'career_path': ['Counselor', 'Clinical Psychologist', 'HR Specialist', 'Professor'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 220, 'catchment': ['Lagos'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 230, 'catchment': ['Oyo'], 'tuition': '₦50,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 200, 'catchment': ['Enugu'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'intrel', 'title': 'International Relations', 'category': 'Social Sciences',
        'description': 'Study global politics, diplomacy, and international affairs.',
        'req_subjects': ['govt', 'econ', 'eng'], 'req_interests': ['law', 'public', 'write'],
        'compulsory_subjects': ['govt', 'eng'],
        'career_path': ['Diplomat', 'Foreign Affairs Officer', 'Ambassador', 'UN Official'],
        'universities': [
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 230, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 235, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 210, 'catchment': ['Kaduna'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== AGRICULTURE ==========
    {
        'id': 'agricsci', 'title': 'Agricultural Science', 'category': 'Agriculture',
        'description': 'Study crop production, livestock, and sustainable farming practices.',
        'req_subjects': ['bio', 'chem', 'agric'], 'req_interests': ['agric', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Farm Manager', 'Agronomist', 'Agricultural Officer', 'Director'],
        'universities': [
            {'name': 'Federal University of Agriculture, Abeokuta (FUNAAB)', 'cutoff': 190, 'catchment': ['Ogun', 'Lagos'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 200, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Ahmadu Bello University (ABU)', 'cutoff': 180, 'catchment': ['Kaduna'], 'tuition': '₦35,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'animsci', 'title': 'Animal Science', 'category': 'Agriculture',
        'description': 'Study animal production, nutrition, and livestock management.',
        'req_subjects': ['bio', 'chem', 'agric'], 'req_interests': ['agric', 'sci', 'care'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Livestock Officer', 'Animal Nutritionist', 'Farm Manager', 'Director'],
        'universities': [
            {'name': 'Federal University of Agriculture, Abeokuta (FUNAAB)', 'cutoff': 180, 'catchment': ['Ogun'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 190, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'fisheries', 'title': 'Fisheries & Aquaculture', 'category': 'Agriculture',
        'description': 'Study fish production, marine biology, and seafood management.',
        'req_subjects': ['bio', 'chem', 'agric'], 'req_interests': ['agric', 'sci', 'build'],
        'compulsory_subjects': ['bio', 'chem'],
        'career_path': ['Fish Farm Manager', 'Aquaculture Specialist', 'Marine Biologist', 'Director'],
        'universities': [
            {'name': 'Federal University of Agriculture, Abeokuta (FUNAAB)', 'cutoff': 175, 'catchment': ['Ogun'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 185, 'catchment': ['Oyo'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== EDUCATION ==========
    {
        'id': 'edumaths', 'title': 'Education (Mathematics)', 'category': 'Education',
        'description': 'Train to become a qualified mathematics teacher.',
        'req_subjects': ['math', 'eng', 'phys'], 'req_interests': ['teach', 'sci', 'build'],
        'compulsory_subjects': ['math', 'eng'],
        'career_path': ['Teacher', 'Head of Department', 'Principal', 'Education Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 190, 'catchment': ['Lagos'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Ibadan (UI)', 'cutoff': 200, 'catchment': ['Oyo'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Adeniran Ogunsanya College of Education', 'cutoff': 150, 'catchment': ['Lagos'], 'tuition': '₦30,000', 'duration': '3 Years (NCE)', 'type': 'college'},
        ]
    },
    {
        'id': 'eduscience', 'title': 'Education (Science)', 'category': 'Education',
        'description': 'Train to become a qualified science teacher.',
        'req_subjects': ['bio', 'chem', 'eng'], 'req_interests': ['teach', 'sci', 'care'],
        'compulsory_subjects': ['bio', 'chem', 'eng'],
        'career_path': ['Teacher', 'Head of Department', 'Principal', 'Education Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 185, 'catchment': ['Lagos'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Nigeria, Nsukka (UNN)', 'cutoff': 180, 'catchment': ['Enugu'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Federal College of Education, Akoka', 'cutoff': 150, 'catchment': ['Lagos'], 'tuition': '₦25,000', 'duration': '3 Years (NCE)', 'type': 'college'},
        ]
    },
    {
        'id': 'eduenglish', 'title': 'Education (English)', 'category': 'Education',
        'description': 'Train to become a qualified English language teacher.',
        'req_subjects': ['eng', 'lit', 'govt'], 'req_interests': ['teach', 'write', 'media'],
        'compulsory_subjects': ['eng', 'lit'],
        'career_path': ['Teacher', 'Head of Department', 'Principal', 'Education Director'],
        'universities': [
            {'name': 'University of Ibadan (UI)', 'cutoff': 195, 'catchment': ['Oyo'], 'tuition': '₦40,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 185, 'catchment': ['Lagos'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
        ]
    },
    # ========== ARCHITECTURE ==========
    {
        'id': 'arch', 'title': 'Architecture', 'category': 'Engineering',
        'description': 'Design buildings and spaces that shape how we live and work.',
        'req_subjects': ['math', 'phys', 'fineArt'], 'req_interests': ['build', 'art', 'sci'],
        'compulsory_subjects': ['math', 'phys'],
        'career_path': ['Intern Architect', 'Architect', 'Senior Architect', 'Principal Architect'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 260, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 250, 'catchment': ['Osun'], 'tuition': '₦50,000', 'duration': '5 Years', 'type': 'university'},
            {'name': 'Covenant University', 'cutoff': 200, 'catchment': [], 'tuition': '₦1,100,000', 'duration': '5 Years', 'type': 'university'},
        ]
    },
    {
        'id': 'estateman', 'title': 'Estate Management', 'category': 'Business',
        'description': 'Manage property, real estate development, and valuations.',
        'req_subjects': ['math', 'econ', 'eng'], 'req_interests': ['money', 'build', 'law'],
        'compulsory_subjects': ['math', 'econ'],
        'career_path': ['Estate Surveyor', 'Property Manager', 'Chief Valuer', 'Director'],
        'universities': [
            {'name': 'University of Lagos (UNILAG)', 'cutoff': 230, 'catchment': ['Lagos'], 'tuition': '₦55,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Obafemi Awolowo University (OAU)', 'cutoff': 220, 'catchment': ['Osun'], 'tuition': '₦45,000', 'duration': '4 Years', 'type': 'university'},
            {'name': 'Yaba College of Technology (YABATECH)', 'cutoff': 165, 'catchment': ['Lagos'], 'tuition': '₦35,000', 'duration': '2 Years (ND)', 'type': 'polytechnic'},
        ]
    },
]

# ─────────────────────────────────────────────
# SYSTEM PROMPT FOR AI CHATBOT
# ─────────────────────────────────────────────
CHATBOT_SYSTEM_PROMPT = """You are Career Compass AI, a knowledgeable and friendly academic advisor specializing in Nigerian university admissions, JAMB/WAEC requirements, and tertiary education. You have deep, current knowledge of Nigerian universities and always provide accurate, up-to-date information.

Your role is to:
1. Help Nigerian students understand their university course options based on their JAMB scores and WAEC grades
2. Provide accurate and current advice about Nigerian universities (federal, state, and private), polytechnics, and colleges of education — including their latest cutoff marks, tuition fees, course durations, and admission requirements
3. Explain course requirements, career prospects, and admission processes in Nigeria
4. Discuss JAMB UTME, Post-UTME, Direct Entry, and O'Level requirements
5. Offer guidance on the best courses based on interests, grades, and career goals
6. Correct or supplement any outdated school information the app may display, using your current knowledge

Key facts to know:
- JAMB scores range from 140-400; most universities require 200+; competitive courses (Medicine, Law, Engineering) typically require 250+
- WAEC grades: A1 (excellent), B2-B3 (very good), C4-C6 (credit/pass), D7-E8-F9 (fail — not accepted for admission)
- English Language and Mathematics are compulsory for ALL courses — minimum C6 required
- Universities in Nigeria: federal (UNILAG, UI, ABU, UNN, OAU, UNIBEN, FUTA, FUTO, FUNAAB, FUPRE etc.), state, and private (Covenant, Babcock, Afe Babalola, Landmark, Pan-Atlantic etc.)
- Polytechnics offer ND (2 years) and HND (2 years) programs — good alternatives for lower JAMB scores
- Colleges of Education offer NCE (3 years) programs
- Post-UTME is a separate screening exam used by universities after JAMB
- Catchment areas are states/regions where universities give admission priority
- JAMB cutoff marks are announced yearly — always clarify the current year's cutoff when answering
- Tuition fees vary widely: federal universities (₦30,000–₦60,000), state universities (₦80,000–₦300,000), private universities (₦500,000–₦3,000,000+)

When a student asks about a specific school:
- Use your current knowledge to give accurate cutoff marks, tuition, course availability, and Post-UTME details
- If the app showed them a school, verify it is correct and add any important details they should know
- Always mention if a school requires Post-UTME and approximately what score is needed
- Mention if the school has catchment area advantages for the student's state

When a student's JAMB score is low (140-199):
- Be honest but encouraging
- Suggest polytechnics, colleges of education, or private universities as alternatives
- Recommend JAMB resit if their score is too low for their dream course

Always be:
- Encouraging but honest about admission competitiveness
- Specific about Nigerian institutions, cut-off marks, and requirements
- Helpful with alternative options if a student's score is low
- Accurate — if you are unsure about a specific current figure, say so and direct them to the school's official website or jamb.gov.ng

Keep responses under 200 words. Use bullet points when listing options. Be warm and motivating.

IMPORTANT: The app's school database may not reflect the most current admission year. Always use your own knowledge to verify or correct school information when a student asks, and remind them to always confirm final details on jamb.gov.ng or the school's official website."""

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "mode": "production", "courses": len(COURSES)})


@app.route('/courses')
def get_courses():
    return jsonify([{'id': c['id'], 'title': c['title'], 'category': c['category']} for c in COURSES])


@app.route('/chat', methods=['POST'])
def chat():
    """AI-powered chatbot using Groq (free tier)"""
    data = request.json
    messages = data.get('messages', [])
    user_context = data.get('userContext', {})

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # Build context string from user data
    # Build context string from user data
    context_str = ""
    if user_context.get('jamb'):
        context_str += f"\n\nStudent profile: JAMB score = {user_context['jamb']}"
    if user_context.get('track'):
        context_str += f", WAEC track = {user_context['track']}"
    if user_context.get('interests'):
        context_str += f", Interests = {', '.join(user_context['interests'])}"
    if user_context.get('topMatches'):
        context_str += f"\nCourses the app matched for this student: {', '.join(user_context['topMatches'])}"
        context_str += f"\nPlease verify these matches are accurate for the student's JAMB score and suggest corrections if needed."

    try:
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=300,
            messages=[
                {"role": "system", "content": CHATBOT_SYSTEM_PROMPT + context_str}
            ] + formatted_messages
        )

        reply_text = response.choices[0].message.content
        return jsonify({'reply': reply_text})

    except Exception as e:
        print(f"Groq error: {e}")
        return jsonify({'error': f'AI service error: {str(e)}'}), 500


# Cache to avoid repeated Groq calls for same course+score combination
university_cache = {}

def get_universities_from_groq(course_title, course_category, jamb_score):
    """Use Groq AI to get accurate current university data for a course"""

    # Return cached result if same course+score was already looked up
    cache_key = f"{course_title}_{jamb_score}"
    if cache_key in university_cache:
        print(f"Cache hit: {cache_key}")
        return university_cache[cache_key]

    try:
        prompt = f"""You are a Nigerian university admissions expert with accurate 2024/2025 knowledge.

For the course "{course_title}" ({course_category}), list Nigerian universities and polytechnics that accept a JAMB score of {jamb_score}.

Return ONLY a valid JSON array. No explanation, no markdown, no extra text. Just raw JSON.

Each object must have exactly these fields:
- "name": full official university name
- "cutoff": integer JAMB cutoff mark for this course at this school
- "tuition": current 2024/2025 annual tuition in Naira like "₦250,000"
- "duration": course duration like "5 Years" or "4 Years" or "2 Years (ND)"
- "type": one of "university", "polytechnic", or "college"
- "catchment": array of Nigerian states this school gives priority to, empty array [] if none

Important rules:
- Only include schools where cutoff is less than or equal to {jamb_score}
- Use accurate 2024/2025 tuition (federal universities now charge ₦150,000-₦300,000+, private universities ₦1,000,000-₦4,000,000+)
- Course duration must be accurate for Nigeria (Medicine=6 years, Law=5 years, Engineering=5 years, Sciences=4 years, Business=4 years etc.)
- Include maximum 6 schools
- If no schools qualify return empty array []

Return only the JSON array, nothing else."""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=800,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Nigerian university data expert. You only return valid JSON arrays. Never return explanations or markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.choices[0].message.content.strip()

        # Clean response in case model adds markdown
        if '```' in response_text:
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()

        # Find JSON array in response
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

        universities = json.loads(response_text)

        if not isinstance(universities, list):
            return []

        # Store in cache
        university_cache[cache_key] = universities
        return universities

    except Exception as e:
        print(f"Groq university lookup error for {course_title}: {e}")
        return []


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_grades = data.get('grades', {})
    user_interests = data.get('interests', [])
    user_jamb = data.get('jamb', 0)

    results = []

    for course in COURSES:
        qualified = True

        # UNIVERSAL RULE: English AND Maths must be at least C6 for ALL courses
        if user_grades.get('eng', 0) < 3:
            qualified = False
        if user_grades.get('math', 0) < 3:
            qualified = False

        # COURSE-SPECIFIC: All compulsory subjects must be at least C6
        if qualified:
            for sub in course.get('compulsory_subjects', []):
                if user_grades.get(sub, 0) < 3:
                    qualified = False
                    break

        if not qualified:
            continue

        # Calculate match score
        score = 0
        for sub in course['req_subjects']:
            g = user_grades.get(sub, 0)
            if g >= 4:
                score += 20
            elif g == 3:
                score += 15
            elif g == 2:
                score += 5

        for interest in course['req_interests']:
            if interest in user_interests:
                score += 15

        if score < 20:
            continue

        # Get accurate universities from Groq AI
        eligible_universities = get_universities_from_groq(
            course['title'],
            course['category'],
            user_jamb
        )

        if not eligible_universities:
            continue

        results.append({
            **course,
            "score": score,
            "universities": eligible_universities
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, port=5000)