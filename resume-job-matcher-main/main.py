from flask import Flask, request, render_template
import os
import uuid
import docx2txt
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',   quiet=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER']      = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB cap

# -------------------------------------------------------
# NLP Tools - initialized once at startup
# -------------------------------------------------------
lemmatizer = WordNetLemmatizer()
STOP_WORDS  = set(stopwords.words('english'))

# -------------------------------------------------------
# ALIAS MAP - normalize all variants to one canonical form
# Solves: "ml" == "machine learning", "ai" == "artificial intelligence"
#         "nlp" == "natural language processing"
# -------------------------------------------------------
SKILL_ALIASES = {
    "ml":                          "machine learning",
    "ai":                          "artificial intelligence",
    "nlp":                         "natural language processing",
    "dl":                          "deep learning",
    "cv":                          "computer vision",
    "gcp":                         "google cloud platform",
    "google cloud":                "google cloud platform",
    "amazon web services":         "aws",
    "microsoft azure":             "azure",
    "js":                          "javascript",
    "ts":                          "typescript",
    "py":                          "python",
    "node":                        "nodejs",
    "node.js":                     "nodejs",
    "postgres":                    "postgresql",
    "mongo":                       "mongodb",
    "mongo db":                    "mongodb",
    "oop":                         "object oriented programming",
    "object oriented":             "object oriented programming",
    "ci cd":                       "ci/cd",
    "cicd":                        "ci/cd",
    "rest":                        "rest api",
    "restful":                     "rest api",
    "restful api":                 "rest api",
    "powerbi":                     "power bi",
    "sk learn":                    "scikit-learn",
    "sklearn":                     "scikit-learn",
    "data science":                "data analytics",
    "data analysis":               "data analytics",
    "analytics":                   "data analytics",
    "statistical analysis":        "statistics",
    "stats":                       "statistics",
    "team work":                   "teamwork",
    "problem-solving":             "problem solving",
    "critical thinking":           "problem solving",
}

# -------------------------------------------------------
# Canonical Skill Dictionary (no duplicates - aliases handle variants)
# -------------------------------------------------------
SKILL_KEYWORDS = {
    "python", "java", "c", "c++", "c#", "r", "go", "rust", "swift",
    "kotlin", "typescript", "scala", "perl", "ruby", "matlab",
    "html", "css", "javascript", "react", "angular", "vue", "nodejs",
    "django", "flask", "fastapi", "spring", "bootstrap", "tailwind",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis",
    "oracle", "nosql", "firebase", "cassandra",
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "computer vision",
    "data analytics", "data engineering", "data visualization",
    "statistics", "big data", "feature engineering", "model evaluation",
    "cloud computing", "aws", "azure", "google cloud platform",
    "docker", "kubernetes", "ci/cd", "devops", "linux",
    "git", "github", "gitlab", "jenkins",
    "pandas", "numpy", "scikit-learn", "tensorflow", "keras",
    "pytorch", "matplotlib", "seaborn", "tableau", "power bi",
    "excel", "spark", "hadoop", "airflow", "dbt",
    "software engineering", "software development", "agile", "scrum",
    "object oriented programming", "rest api", "graphql",
    "microservices", "system design", "testing", "debugging",
    "version control",
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "research", "documentation",
}

# -------------------------------------------------------
# Text Extraction
# -------------------------------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception:
        text = ""
    return text

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception:
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ""

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    return ""

# -------------------------------------------------------
# NLP Layer 1 - Alias Normalization
# Longest aliases replaced first to prevent phrase fragmentation.
# e.g. "machine learning" replaced before "machine" could be touched.
# -------------------------------------------------------
def normalize_aliases(text):
    text = text.lower()
    for alias, canonical in sorted(SKILL_ALIASES.items(),
                                   key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(alias) + r'\b'
        text = re.sub(pattern, canonical, text)
    return text

# -------------------------------------------------------
# NLP Layer 2 - Lemmatization + Stopword Removal
# -------------------------------------------------------
def preprocess_text(text):
    text = normalize_aliases(text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in STOP_WORDS and len(word) > 1
    ]
    return ' '.join(tokens)

# -------------------------------------------------------
# NLP Layer 3 - Rule-Based Skill Extraction
# Multi-word skills matched first (longest to shortest)
# to prevent substring contamination.
# -------------------------------------------------------
def extract_skills(text):
    found  = set()
    text   = normalize_aliases(text.lower())
    sorted_skills = sorted(SKILL_KEYWORDS, key=lambda s: len(s.split()), reverse=True)
    for skill in sorted_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.add(skill)
    return sorted(found)

# -------------------------------------------------------
# NLP Layer 4 - TF-IDF Cosine Similarity (batch-normalized)
#
# WHY normalization is needed:
#   Raw cosine on full documents gives 5-15% because TF-IDF
#   vectors are high-dimensional and sparse. This is mathematically
#   expected - NOT poor matching.
#
# Fix: run TF-IDF on ALL resumes + job together (shared vocabulary),
#   then MIN-MAX NORMALIZE so best resume = 100, worst = 0.
#   Result: a reliable relative ranking signal, not a dragged-down score.
# -------------------------------------------------------
def tfidf_cosine_scores_normalized(job_processed, resumes_processed):
    if not job_processed.strip():
        return [0.0] * len(resumes_processed)
    try:
        corpus       = [job_processed] + resumes_processed
        vectorizer   = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        job_vec      = tfidf_matrix[0:1]
        resume_vecs  = tfidf_matrix[1:]
        raw_scores   = cosine_similarity(job_vec, resume_vecs)[0]
        min_s = raw_scores.min()
        max_s = raw_scores.max()
        if max_s == min_s:
            return [50.0] * len(raw_scores)
        return [
            round(((s - min_s) / (max_s - min_s)) * 100, 2)
            for s in raw_scores
        ]
    except Exception:
        return [0.0] * len(resumes_processed)

# -------------------------------------------------------
# NLP Layer 5 - Jaccard Similarity on Skill Sets
# Applied on extracted SKILL SETS only (not full document text).
# Alias normalization ensures "ml" and "machine learning"
# are the same token - no double counting.
# -------------------------------------------------------
def jaccard_skill_similarity(job_skills, resume_skills):
    set1 = set(job_skills)
    set2 = set(resume_skills)
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union        = set1 | set2
    return round((len(intersection) / len(union)) * 100, 2)

# -------------------------------------------------------
# Hybrid Score Combiner
#
# Weights:
#   Keyword Match  60%  - primary signal, domain-specific, precise
#   TF-IDF Cosine  25%  - relative contextual ranking within batch
#   Jaccard        15%  - set-level skill vocabulary overlap
#
# TF-IDF is weighted lower (25%) because it is a relative signal.
# Keyword match drives the score as it is absolute and precise.
# -------------------------------------------------------
def compute_hybrid_score(keyword_score, tfidf_norm_score, jaccard_score):
    hybrid = (0.60 * keyword_score) + (0.25 * tfidf_norm_score) + (0.15 * jaccard_score)
    return round(hybrid, 2)

# -------------------------------------------------------
# Routes
# -------------------------------------------------------
@app.route("/")
def matchresume():
    return render_template("matchresume.html",
                           top_resumes=[], similarity_scores=[],
                           matched_keywords=[], top_3_resumes=[],
                           top_3_scores=[], tfidf_scores=[],
                           keyword_scores=[], jaccard_scores=[],
                           message=None)

@app.route("/matcher", methods=["POST"])
def matcher():
    job_description_raw = request.form.get("job_description", "").strip()
    resume_files        = request.files.getlist("resumes")

    if not job_description_raw or not resume_files:
        return render_template("matchresume.html",
                               message="Please upload resumes and enter a job description.",
                               top_resumes=[], similarity_scores=[],
                               matched_keywords=[], top_3_resumes=[],
                               top_3_scores=[], tfidf_scores=[],
                               keyword_scores=[], jaccard_scores=[])

    processed_job = preprocess_text(job_description_raw)
    job_skills    = extract_skills(job_description_raw)

    resume_names           = []
    resume_processed_texts = []
    resume_skills_list     = []
    temp_paths             = []

    for resume in resume_files:
        safe_name   = secure_filename(resume.filename)
        unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
        path        = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        resume.save(path)
        temp_paths.append(path)
        resume_names.append(safe_name)

        raw_text       = extract_text(path)
        processed_text = preprocess_text(raw_text)
        skills         = extract_skills(raw_text)

        resume_processed_texts.append(processed_text)
        resume_skills_list.append(skills)

    # Layer 4: TF-IDF on entire batch at once
    tfidf_norm_scores = tfidf_cosine_scores_normalized(processed_job, resume_processed_texts)

    matched_keywords_list = []
    keyword_scores_list   = []
    jaccard_scores_list   = []
    hybrid_scores_list    = []

    for skills, tfidf_score in zip(resume_skills_list, tfidf_norm_scores):
        matched_kws = sorted(set(skills) & set(job_skills))
        matched_keywords_list.append(matched_kws)

        kw_score  = round((len(matched_kws) / len(job_skills)) * 100, 2) if job_skills else 0.0
        jac_score = jaccard_skill_similarity(job_skills, skills)
        h_score   = compute_hybrid_score(kw_score, tfidf_score, jac_score)

        keyword_scores_list.append(kw_score)
        jaccard_scores_list.append(jac_score)
        hybrid_scores_list.append(h_score)

    for path in temp_paths:
        try:
            os.remove(path)
        except Exception:
            pass

    sorted_indices = sorted(range(len(hybrid_scores_list)),
                            key=lambda i: hybrid_scores_list[i],
                            reverse=True)

    top_resumes     = [resume_names[i]          for i in sorted_indices]
    top_scores      = [hybrid_scores_list[i]    for i in sorted_indices]
    sorted_keywords = [matched_keywords_list[i] for i in sorted_indices]
    sorted_tfidf    = [tfidf_norm_scores[i]     for i in sorted_indices]
    sorted_kw_sc    = [keyword_scores_list[i]   for i in sorted_indices]
    sorted_jac      = [jaccard_scores_list[i]   for i in sorted_indices]

    return render_template(
        "matchresume.html",
        message="Resume Evaluation Complete",
        top_resumes=top_resumes,
        similarity_scores=top_scores,
        matched_keywords=sorted_keywords,
        top_3_resumes=top_resumes[:3],
        top_3_scores=top_scores[:3],
        tfidf_scores=sorted_tfidf,
        keyword_scores=sorted_kw_sc,
        jaccard_scores=sorted_jac
    )

# -------------------------------------------------------
# Run App
# -------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(host="0.0.0.0", port=10000)