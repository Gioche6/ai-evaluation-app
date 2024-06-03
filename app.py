from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import psycopg2
import psycopg2.extras
from decimal import Decimal

app = Flask(__name__)

# Check for DATABASE_URL environment variable to decide on using PostgreSQL or SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

main_metrics = [
    'Bias Detection and Mitigation', 'Explainability and Transparency',
    'Ethical Guidelines', 'Socio-Cultural Relevance', 'Governance and Accountability',
    'Continuous Monitoring and Evaluation'
]

categories = {
    'Bias Detection and Mitigation': {
        'Representation in Training Data': {
            1: 'Poor representation of diverse demographic groups.',
            2: 'Minimal representation with significant gaps.',
            3: 'Moderate representation but still lacking in some areas.',
            4: 'Good representation with minor gaps.',
            5: 'Excellent representation, comprehensively inclusive of diverse groups.'
        },
        'Inclusion of Underrepresented Groups': {
            1: 'Ineffective inclusion of marginalized groups.',
            2: 'Minimal efforts with limited impact.',
            3: 'Moderate inclusion with noticeable improvements.',
            4: 'Effective inclusion with significant positive impact.',
            5: 'Highly effective inclusion, systematically addressing underrepresentation.'
        },
        'Addressing Known Gaps in Diversity': {
            1: 'Not addressed.',
            2: 'Poorly addressed with minimal impact.',
            3: 'Moderately addressed with some impact.',
            4: 'Well addressed with significant improvements.',
            5: 'Fully addressed with comprehensive measures in place.'
        },
        'Performance Disparities Across Demographic Groups': {
            1: 'Significant disparities.',
            2: 'Moderate disparities.',
            3: 'Some disparities but manageable.',
            4: 'Minor disparities.',
            5: 'No disparities, highly consistent performance.'
        },
        'Addressing Performance Disparities': {
            1: 'Ineffective strategies.',
            2: 'Minimally effective strategies.',
            3: 'Moderately effective strategies.',
            4: 'Effective strategies with noticeable improvements.',
            5: 'Highly effective strategies, disparities well-managed.'
        },
        'Effectiveness of Bias Mitigation Techniques': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Ongoing Efforts to Update Bias Mitigation': {
            1: 'Poor efforts.',
            2: 'Minimal efforts.',
            3: 'Moderate efforts.',
            4: 'Good efforts.',
            5: 'Excellent efforts, continuously updated.'
        }
    },
    'Explainability and Transparency': {
        'Use of Interpretable Models or Techniques': {
            1: 'Poor use of interpretable models.',
            2: 'Minimal use, not easily accessible.',
            3: 'Moderate use, somewhat accessible.',
            4: 'Good use, accessible.',
            5: 'Excellent use, highly accessible and understandable.'
        },
        'Tailoring to Technical Literacy and Cultural Norms': {
            1: 'Poor tailoring.',
            2: 'Minimal tailoring.',
            3: 'Moderate tailoring.',
            4: 'Good tailoring.',
            5: 'Excellent tailoring.'
        },
        'Communication of Explanations': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Comprehensive and Accessible Documentation': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Explanation Tools Tailored to Local Contexts': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Accessibility of Explanation Tools': {
            1: 'Poor accessibility.',
            2: 'Minimal accessibility.',
            3: 'Moderate accessibility.',
            4: 'Good accessibility.',
            5: 'Excellent accessibility.'
        },
        'User Understanding of AI Decisions': {
            1: 'Poor understanding.',
            2: 'Minimal understanding.',
            3: 'Moderate understanding.',
            4: 'Good understanding.',
            5: 'Excellent understanding.'
        },
        'Measures to Build and Maintain Trust': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Feedback Mechanisms for Comprehension and Trust': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        }
    },
    'Ethical Guidelines': {
        'Adherence to Ethical Guidelines': {
            1: 'Poor adherence.',
            2: 'Minimal adherence.',
            3: 'Moderate adherence.',
            4: 'Good adherence.',
            5: 'Excellent adherence.'
        },
        'Integration of Ethical Principles': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Exceeding Ethical Standards': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Effectiveness of Ethical Review Processes': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Review and Update of Ethical Processes': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Inclusivity in Ethical Compliance': {
            1: 'Not inclusive.',
            2: 'Minimally inclusive.',
            3: 'Moderately inclusive.',
            4: 'Inclusive.',
            5: 'Highly inclusive.'
        },
        'Transparency in Data Usage and Consent': {
            1: 'Not transparent.',
            2: 'Minimally transparent.',
            3: 'Moderately transparent.',
            4: 'Transparent.',
            5: 'Highly transparent.'
        },
        'Effectiveness of Data Protection Measures': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Implementation of Data Sovereignty Provisions': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        }
    },
    'Socio-Cultural Relevance': {
        'Integration of Local Knowledge and Practices': {
            1: 'Poor integration.',
            2: 'Minimal integration.',
            3: 'Moderate integration.',
            4: 'Good integration.',
            5: 'Excellent integration.'
        },
        'Effectiveness of Stakeholder Consultation': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Respect for Cultural Practices and Values': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Adaptability to Socio-Economic Contexts': {
            1: 'Not adaptable.',
            2: 'Minimally adaptable.',
            3: 'Moderately adaptable.',
            4: 'Adaptable.',
            5: 'Highly adaptable.'
        },
        'Functionality in Resource-Constrained Settings': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Testing and Validation Across Settings': {
            1: 'Poor testing/validation.',
            2: 'Minimal testing/validation.',
            3: 'Moderate testing/validation.',
            4: 'Good testing/validation.',
            5: 'Excellent testing/validation.'
        },
        'Stakeholder Engagement Mechanisms': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Collection and Integration of Stakeholder Feedback': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Implementation and Communication of Updates Based on Feedback': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        }
    },
    'Governance and Accountability': {
        'Clarity of Roles and Responsibilities': {
            1: 'Poor clarity.',
            2: 'Minimal clarity.',
            3: 'Moderate clarity.',
            4: 'Good clarity.',
            5: 'Excellent clarity.'
        },
        'Comprehensiveness of Governance Framework': {
            1: 'Not comprehensive.',
            2: 'Minimally comprehensive.',
            3: 'Moderately comprehensive.',
            4: 'Comprehensive.',
            5: 'Highly comprehensive.'
        },
        'Effectiveness of Accountability Frameworks': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Regular Audits and Assessments': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Accessibility and Effectiveness of Grievance Mechanisms': {
            1: 'Inaccessible/Ineffective.',
            2: 'Minimally accessible/Effective.',
            3: 'Moderately accessible/Effective.',
            4: 'Accessible/Effective.',
            5: 'Highly accessible/Effective.'
        },
        'Timeliness and Satisfactory Resolution of Grievances': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Transparency in Addressing Grievances': {
            1: 'Not transparent.',
            2: 'Minimally transparent.',
            3: 'Moderately transparent.',
            4: 'Transparent.',
            5: 'Highly transparent.'
        }
    },
    'Continuous Monitoring and Evaluation': {
        'Implementation of Continuous Monitoring Processes': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Effectiveness of Monitoring Tools and Technologies': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Frequency of Updates and Maintenance': {
            1: 'Infrequent.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Frequent.',
            5: 'Very frequent.'
        },
        'Appropriateness of Update and Maintenance Schedules': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Effectiveness of Emergency Update Protocols': {
            1: 'Ineffective.',
            2: 'Minimally effective.',
            3: 'Moderately effective.',
            4: 'Effective.',
            5: 'Highly effective.'
        },
        'Implementation of Feedback Loops for Improvement': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Regular Reviews and Updates Based on Feedback': {
            1: 'Poor.',
            2: 'Minimal.',
            3: 'Moderate.',
            4: 'Good.',
            5: 'Excellent.'
        },
        'Adaptability and Responsiveness to Changes': {
            1: 'Not adaptable.',
            2: 'Minimally adaptable.',
            3: 'Moderately adaptable.',
            4: 'Adaptable.',
            5: 'Highly adaptable.'
        }
    }
}
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form')
def form():
    return render_template('form.html', categories=categories)

@app.route('/results')
def results():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT title, category, score FROM evaluations')
    rows = c.fetchall()
    conn.close()
    
    results_dict = {}
    for row in rows:
        title, category, score = row
        if title not in results_dict:
            results_dict[title] = {metric: None for metric in main_metrics}
            results_dict[title]['Overall'] = None  # Initialize Overall key
        results_dict[title][category] = score
    
    results_list = [
        (title, *[scores[metric] for metric in main_metrics], scores['Overall'])
        for title, scores in results_dict.items()
    ]
    
    return render_template('results_list.html', results=results_list, metrics=main_metrics)

@app.route('/calculate', methods=['POST'])
def calculate():
    form_data = request.form
    title = form_data['title']
    scores = {category: [] for category in main_metrics}

    for category in main_metrics:
        for criterion in categories[category]:
            if criterion in form_data:
                scores[category].append(int(form_data[criterion]))

    averages = {category: round(sum(scores[category]) / len(scores[category]), 2) for category in main_metrics}
    overall_score = round(sum(averages.values()) / len(averages), 2)

    conn = get_db_connection()
    c = conn.cursor()
    for category, average in averages.items():
        c.execute('INSERT INTO evaluations (title, category, score) VALUES (%s, %s, %s)', (title, category, average))
    c.execute('INSERT INTO evaluations (title, category, score) VALUES (%s, %s, %s)', (title, 'Overall', overall_score))
    conn.commit()
    conn.close()

    return render_template('summary.html', title=title, averages=averages, overall_score=overall_score)

@app.route('/radar/<title>')
def radar(title):
    conn = None
    data = []
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute('SELECT category, score FROM evaluations WHERE title = %s', (title,))
        rows = c.fetchall()
        for row in rows:
            category, score = row
            if isinstance(score, Decimal):
                score = float(score)  # Convert Decimal to float
            data.append({'category': category, 'score': score})
        c.close()
        print(f"Fetched radar data for {title}: {data}")  # Logging fetched data
    except Exception as e:
        print(f"Error fetching radar data: {e}")
    finally:
        if conn:
            conn.close()
    
    if not data:
        return "No data found for the specified title.", 404

    return render_template('radar.html', title=title, radar_data=data)



@app.route('/api/dashboard_data')
def dashboard_data():
    conn = None
    data = []
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute('SELECT title, category, score FROM evaluations')
        rows = c.fetchall()
        for row in rows:
            title, category, score = row
            if isinstance(score, Decimal):
                score = float(score)  # Convert Decimal to float
            data.append({'title': title, 'category': category, 'score': score})
        c.close()
        print(f"Fetched dashboard data: {data}")  # Logging fetched data
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
    finally:
        if conn:
            conn.close()
    
    return jsonify(data)

@app.route('/delete_result', methods=['POST'])
def delete_result():
    title = request.form['title']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM evaluations WHERE title = %s', (title,))
    conn.commit()
    conn.close()
    return redirect(url_for('results'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

if __name__ == '__main__':
    app.run(debug=True)