from flask import Flask, render_template, request, redirect, url_for
import git

app = Flask(__name__)

REPO_PATH = "C:/Users/brene/OneDrive/Documentos/proyecto personal/pruebas de git"
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

@app.route("/sync", methods=["POST"])
def sync_repo():
    sync_option = request.form.get("sync_option")
    branch_name = request.form.get("branch_name", None)
    
    origin = repo.remote(name='origin')
    
    try:
        # Sincronizar en la rama actual
        if sync_option == "current_branch":
            repo.git.pull('origin', repo.active_branch.name)
        
        # Cambiar de rama
        elif sync_option == "switch_branch":
            branch = request.form.get("branch")
            repo.git.checkout(branch)
            repo.git.pull('origin', branch)
        
        # Crear una nueva rama y sincronizar
        elif sync_option == "new_branch":
            if branch_name:
                repo.git.checkout('-b', branch_name)  # Crear y cambiar a la nueva rama
                repo.git.pull('origin', branch_name)
    
    except git.exc.GitCommandError as e:
        return f"Error: {str(e)}"
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
