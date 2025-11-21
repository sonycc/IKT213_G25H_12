
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

## Run Python Model Trainer


The Python Model Trainer cna be run as configured but it is advicable to look into the configurable variables before doing so:


```ini
SEED          = 42                  | Random seed, same seed ensures same results.
IMG_SIZE      = 224                 | Sets the x*y image size to use
EPOCHS        = 10                  | How many passes over the training set one does
BATCH_TRAIN   = 16                  | Number of samples per training set
BATCH_VAL     = 32                  | Numer of samples ber validation set
LR            = 1e-3                | Learning weight, defines how much of the "new" data influenses the "old" data
NUM_WORKERS   = 16                  | Number of CPU threads we use, recomended is to use as many threads as you have CPU cores.
VAL_SPLIT     = 0.15                | The fraction of the training data to use as validation data if no validation data exsists.
USE_TEST_AS_VAL_IF_NO_VAL = False   | Use the test/ folder as validation if val/ is missing. Should usually be False to keep test data separate.
USE_GRAY_DUPLICATE_AUG = True       | adds grayscale copies of training images to the dataset for augmentation.
USE_ROTATE_DUPLICATE_AUG = True     | adds rotated copies of images to the training dataset.
```


Follow all the steps above but instead you need to start:
```bash
python ../FishApp.PythonModel/train_cod_classifier.py
```


## Run DotNet UI

Then to launch the UI you simply build and run the project files form the root folder.

```bash
dotnet restore
dotnet build
dotnet run
```

the project file should handle the rest. if you encounter an error you can try to run it manually:

```bash
dotnet run --project .\FishAppUI\FishAppUI.csproj
```


