# Migration vers Label Studio SDK 2.0.15

## Changements principaux

La version 2.0.15 du SDK Label Studio a introduit des changements importants dans l'API.

### Ancien SDK (< 2.0)
```python
from label_studio_sdk import Client

ls = Client(url="http://localhost:8080", api_key="YOUR_KEY")
project = ls.get_project(PROJECT_ID)
tasks = project.get_tasks()
project.import_tasks(tasks_list)
```

### Nouveau SDK (2.0.15+)
```python
from label_studio_sdk import LabelStudio

client = LabelStudio(base_url="http://localhost:8080", api_key="YOUR_KEY")
project = client.projects.get(id=PROJECT_ID)
tasks = client.tasks.list(project=project.id)
client.tasks.create_many(project=project.id, tasks=tasks_list)
```

## Changements appliqués

### 1. Import (`scripts/import_to_label_studio.py`)

**Avant:**
```python
from label_studio_sdk import Client
ls = Client(...)
project = ls.get_project(id)
existing_tasks = project.get_tasks()
project.import_tasks(tasks)
```

**Après:**
```python
from label_studio_sdk import LabelStudio
client = LabelStudio(base_url=..., api_key=...)
project = client.projects.get(id=id)
existing_tasks = client.tasks.list(project=project.id)

# Créer les tâches une par une
for task in tasks:
    client.tasks.create(project=project.id, data=task['data'], meta=task.get('meta'))
```

### 2. Export (`scripts/export_from_label_studio.py`)

**Avant:**
```python
from label_studio_sdk import Client
ls = Client(...)
project = ls.get_project(id)
tasks = project.get_tasks()
```

**Après:**
```python
from label_studio_sdk import LabelStudio
client = LabelStudio(base_url=..., api_key=...)
project = client.projects.get(id=id)
tasks_obj = client.tasks.list(project=project.id)
tasks = [task.model_dump() for task in tasks_obj]
```

## Points importants

### 1. Les tâches sont maintenant des objets
Dans la v2.0.15, `client.tasks.list()` retourne des objets `Task` au lieu de dictionnaires. Pour les convertir en dictionnaires (pour compatibilité avec le reste du code):

```python
tasks = [task.model_dump() for task in tasks_obj]
# ou si model_dump() n'existe pas:
tasks = [task.dict() for task in tasks_obj]
```

### 2. Accès aux attributs
Les objets Task ont des attributs accessibles directement:
```python
for task in tasks_obj:
    filename = task.data.get('filename')  # Pas task['data']
```

### 3. Création de tâches
La méthode `project.import_tasks()` n'existe plus. Il n'y a pas non plus de `create_many()`.
Il faut créer les tâches une par une:
```python
# Pour chaque tâche
for task in tasks_to_import:
    client.tasks.create(
        project=project.id,
        data=task['data'],
        meta=task.get('meta')
    )
```

### 4. Informations du projet
Au lieu de `project.get_params()['task_number']`, utilisez directement:
```python
project.task_number
```

## Problèmes connus et solutions

### Images ne s'affichent pas dans Label Studio

**Symptôme**: Message d'erreur "There was an issue loading URL from $image value"

**Cause**: Label Studio ne peut pas afficher directement les PDFs encodés en base64 avec le tag `<image>`

**Solution**: Les PDFs sont maintenant automatiquement convertis en images PNG lors de l'import. Le script `import_to_label_studio.py` utilise PyMuPDF pour convertir la première page de chaque PDF en image haute résolution.

```python
# Conversion automatique PDF → PNG
def pdf_to_image_base64(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]  # Première page
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
    img_bytes = pix.tobytes("png")
    # ... encoder en base64
```

## Tests

Pour vérifier que tout fonctionne:

```bash
# Vérifier la version
python -c "import label_studio_sdk; print(label_studio_sdk.__version__)"

# Tester l'import
python scripts/import_to_label_studio.py

# Tester l'export
python scripts/export_from_label_studio.py
```

## Documentation officielle

- [Label Studio SDK Documentation](https://labelstud.io/sdk/)
- [API Reference](https://labelstud.io/api)
