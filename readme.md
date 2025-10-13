
# Run Project


## Run Python Backend
To create the virtual enviorment you need to install and activate it. 
Use the packages in the requirements.txt file to easily do this.

```bash
cd FishApp.PythonBackend
python -m venv venv        # Create venv
source venv/bin/activate   # Activate (use venv\Scripts\activate on Windows)
pip install -r requirements.txt  # Install deps
python main.py             # Run app
```
After running this you should be able to access the backend by either 0.0.0.0:5000/ping or 127.0.0.1:5000/ping



## Run DotNet UI

Then to launch the UI you simply build and run the project files.

```bash
dotnet build
dotnet run --project .\FishAppUI\FishAppUI.csproj
```


# Use the program
The current proof of consept is extremely simple.

* **Select Image** – Opens a window to choose an image from your computer.
* **Upload Image** – Uploads the selected image to the Python backend.
* **Rotate X** – Rotates the image by *X* degrees.
* **Grayscale** – Converts the image to grayscale.