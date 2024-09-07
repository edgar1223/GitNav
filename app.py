from flask import Flask, render_template, request, redirect, url_for
import git

app = Flask(__name__)

REPO_PATH = "C:/Users/brene/OneDrive/Documentos/residencia/sigaFinal"
repo = git.Repo(REPO_PATH)

@app.route("/", methods=["GET", "POST"])
def index():
    modified_files = [item.a_path for item in repo.index.diff(None)]
    
    branches = repo.git.branch('--all').split('\n')
    current_branch = repo.git.rev_parse('--abbrev-ref', 'HEAD')
    
    if request.method == "POST":
        commit_type = request.form.get("commit_type")
        description = request.form.get("description")
        branch_name = request.form.get("branch_name")
        
        if 'new_branch' in request.form:
            repo.git.checkout('HEAD', b=branch_name)
        
        if 'checkout_branch' in request.form:
            repo.git.checkout(branch_name)
        
        commit_message = f"{commit_type}: {description}"
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        
        return redirect(url_for('index'))
    
    return render_template("index.html", modified_files=modified_files, branches=branches, current_branch=current_branch)

@app.route("/history")
def history():
    commits = list(repo.iter_commits('HEAD'))
    return render_template("history.html", commits=commits)

if __name__ == "__main__":
    app.run(debug=True)
