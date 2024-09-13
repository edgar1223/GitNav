from flask import Flask, render_template, request, redirect, url_for
import git

app = Flask(__name__)

# Ruta del repositorio local
REPO_PATH = "C:/Users/brene/OneDrive/Documentos/proyecto personal/GitNav"
repo = git.Repo(REPO_PATH)

# Ruta principal - Hacer commit
@app.route("/", methods=["GET", "POST"])
def index():
    # Obtener archivos modificados
    modified_files = [item.a_path for item in repo.index.diff(None)]
    
    if request.method == "POST":
        # Obtener archivos seleccionados, tipo de commit y descripción
        selected_files = request.form.getlist("selected_files")
        commit_type = request.form.get("commit_type")
        description = request.form.get("description")
        
        # Agregar archivos seleccionados al commit
        if selected_files:
            for file in selected_files:
                repo.git.add(file)
        
        # Construir mensaje de commit y hacer commit
        commit_message = f"{commit_type}: {description}"
        repo.index.commit(commit_message)
        
        # Hacer push al repositorio remoto
        origin = repo.remote(name='origin')
        origin.push()
        
        return redirect(url_for('index'))  # Redirigir a la página principal
    
    return render_template("index.html", modified_files=modified_files)

# Ruta para crear una nueva rama
@app.route("/create_branch", methods=["GET", "POST"])
def create_branch():
    if request.method == "POST":
        branch_name = request.form.get("branch_name")  # Obtener el nombre de la rama
        repo.git.checkout('HEAD', b=branch_name)  # Crear y cambiar a la nueva rama
        return redirect(url_for('index'))  # Redirigir a la página principal

    # Obtener todas las ramas
    branches = repo.git.branch('--sort=-committerdate').split('\n')
    current_branch = repo.active_branch.name  # Rama actual
    return render_template("create_branch.html", branches=branches, current_branch=current_branch)

# Ruta para ver el historial de commits
@app.route("/history")
def history():
    # Obtener todos los commits en la rama actual
    commits = list(repo.iter_commits('HEAD'))
    return render_template("history.html", commits=commits)

# Ruta para sincronizar el repositorio
@app.route("/sync", methods=["GET", "POST"])
def sync_repo():
    if request.method == "POST":
        sync_option = request.form.get("sync_option")
        branch_name = request.form.get("branch", None)
        
        # Obtener el repositorio remoto
        origin = repo.remote(name='origin')
        
        if sync_option == "current_branch":
            # Hacer pull en la rama actual
            origin.pull()
        
        elif sync_option == "switch_branch" and branch_name:
            # Cambiar a la rama seleccionada
            repo.git.checkout(branch_name)
            origin.pull()
        
        elif sync_option == "new_branch":
            new_branch_name = request.form.get("branch_name")
            if new_branch_name:
                # Crear y cambiar a la nueva rama, luego hacer pull
                repo.git.checkout('HEAD', b=new_branch_name)
                origin.pull()
        
        return redirect(url_for('index'))  # Redirigir a la página principal
    
    # Obtener las ramas disponibles para mostrar en el formulario de sincronización
    branches = repo.git.branch().split('\n')
    branches = [branch.strip() for branch in branches]
    
    return render_template("sync.html", branches=branches)

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
