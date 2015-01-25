from flask import Flask, render_template, request, redirect, session
import requests, random, string
import os
from werkzeug import secure_filename
app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['java', 'zip'])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=['POST'])
def process_java():
    #Make a randomly generated directory for java compilation
    staticFilepath = 'javaComp/' + random.choice(string.letters) + random.choice(string.letters) + random.choice(string.letters) + '/'

    d = os.path.dirname(staticFilepath)
    if not os.path.exists(d):
        os.makedirs(d)

    #If directory already exists, throw an error
    else:
        return render_template("error.html", message="Oh no D:! Something went wrong :( Please try again!")

    file = request.files['java']
    filename = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(staticFilepath, filename))
    else:
        return render_template("error.html", message="Oh no D:! Something went wrong :( Please try again!")

    filename = unzip(file, staticFilepath)

    #Compile Java, catch any errors
    bashCommand = "javac " + filename;
    print bashCommand
    import subprocess
    try:
        subprocess.check_output(bashCommand.split(), stderr=subprocess.STDOUT, cwd=staticFilepath)
    except subprocess.CalledProcessError as err:
        output = err.output

        #Clean Up
        import shutil
        shutil.rmtree(staticFilepath)
        return render_template("success.html", compiler_msg=output)

    #Clean Up
    import shutil
    shutil.rmtree(staticFilepath)
    return render_template("success.html", compiler_msg="No Errors!")

@app.route("/back", methods=['GET'])
def back_to_input():
    return render_template("index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def unzip(file, filepath):
    if ".zip" in file.filename:
        bashCommand = "unzip " + file.filename;
        import subprocess
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd=filepath)

        #Get names of java files in dir
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [ f for f in listdir(filepath) if isfile(join(filepath,f)) ]
        res = ""

        for file in onlyfiles:
            if ".java" in file:
                res += file + " "

        return res
    else:
        return file.filename

if __name__ == "__main__":
    app.run(debug="true")
