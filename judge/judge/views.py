from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import os
import subprocess
import re

UPLOAD_FOLDER = os.getcwd() + '/submissions/'
ALLOWED_LANGUAGES = {"py2": ".py",
                     "py3": ".py",
                     "c": ".c",
                     "cpp": ".cpp",
                     "java": ".java"}


def run_command(command, file_location='', _compile=False):
    response = True
    error = ''
    if _compile:
        try:
            subprocess.check_output(command + " " + file_location.strip(),
                                    shell=True,
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            response = False
            error = e.output.decode('utf-8').replace(UPLOAD_FOLDER, "")
    else:
        try:
            subprocess.check_output(command + " " + file_location.strip() + " < " + os.path.join(UPLOAD_FOLDER, "input.txt") + " > code_output.txt",
                                    shell=True,
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            response = False
            error = e.output.decode('utf-8').replace(UPLOAD_FOLDER, "")
    return (response, error)


def compile_code(request):
    response = True
    error = None
    language = request.POST.get("language")
    if language == "cpp":
        response, string = run_command("g++",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]),
                                       _compile=True)
    elif language == "c":
        response, string = run_command("gcc",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]),
                                       _compile=True)
    elif language == "py2":
        response, string = run_command("python2 -m py_compile",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]),
                                       _compile=True)
    elif language == "py3":
        response, string = run_command("python3 -m py_compile",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]),
                                       _compile=True)
    else:
        response = False
        string = "This language is not supported."
    return HttpResponse(json.dumps({"response": response, "message": string.replace("<", "&lt;").replace(">", "&gt;")}))


def detect_language(code, ext):
    if ext == "java":
        return "java"
    elif ext == "c":
        return "c"
    elif ext == "cpp":
        return "cpp"
    elif ext == "py":
        if re.findall(r'print *\(.*\)', code):
            return "py2" if re.findall(r'xrange', code) else "py3"
        else:
            return "py2"
    else:
        return None


def execute_code(request):
    response = True
    error = None
    language = request.POST.get("language")
    if language == "cpp" or language == "c":
        response, string = run_command("./a.out")
    elif language == "py2":
        response, string = run_command("python2",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]))
    elif language == "py3":
        response, string = run_command("python3",
                                       file_location=os.path.join(
                                           UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]))
    else:
        response = False
        string = "This language is not supported."
    print(response, string)
    return HttpResponse(json.dumps({"response": response, "message": string.replace("<", "&lt;").replace(">", "&gt;")}))


def home(request):
    return render(request, 'index.html')


@ensure_csrf_cookie
def upload_code(request):
    response = True
    error = None
    ext = request.POST.get("ext")
    file = request.FILES.get("fileupload")
    if ext:
        if file:
            code = file.read().decode("utf-8")
            language = detect_language(code, ext)
            return HttpResponse(json.dumps({"response": response, "code": code, "language": language}))
        else:
            response = False
            error = "File not found!"
    else:
        response = False
        error = "Something wrong with extension"
    return HttpResponse(json.dumps({"response": response, "error": error}))


@ensure_csrf_cookie
def upload_files(request):
    response = True
    error = None
    input_file = request.FILES.get("inputFile")
    output_file = request.FILES.get("outputFile")
    code = request.POST.get("code")
    language = request.POST.get("language")
    if input_file:
        if output_file:
            if code:
                if language:
                    try:
                        if not os.path.exists(UPLOAD_FOLDER):
                            os.mkdir(UPLOAD_FOLDER)
                        with open(os.path.join(UPLOAD_FOLDER, "input.txt"), 'w+') as f:
                            for chunk in input_file.chunks():
                                f.write(chunk.decode('utf-8'))
                        with open(os.path.join(UPLOAD_FOLDER, "output.txt"), 'w+') as f:
                            for chunk in output_file.chunks():
                                f.write(chunk.decode('utf-8'))
                        with open(os.path.join(UPLOAD_FOLDER, "code" + ALLOWED_LANGUAGES[language]), 'w+') as f:
                            f.write(code)
                    except:
                        response = False
                        error = "Unexpected error occurred!"
                else:
                    response = False
                    error = "Language selection error!"
            else:
                response = False
                error = "Code upload error!"
        else:
            response = False
            error = "Output file not found!"
    else:
        response = False
        error = "Input file not found!"
    return HttpResponse(json.dumps({"response": response, "error": error}))
