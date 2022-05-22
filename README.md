# JEE Practice

This application provides you a way to practice for Computer-based Tests (CBT) in a way that gives you complete control over your data.

The functionality is provided as a browser-based Flask application that runs locally on your own machine.

**This project is not affiliated with NTA, VIT, IIIT, or any of the entities whose test paper patterns are used here, in any way, shape, or form.**

## Key concepts
* You can sit one **test**/**exam** at a time.
* Each exam will have one or more **sections**.
* Each section will have one or more **questions**.
* All the questions within a section will be of the same type (for example, Multiple Choice Questions).
* Within each section, all questions will follow the same marking system (for example, +4 marks for a correct answer, -1 for a wrong answer, and 0 if it was not attempted).
* You can either design your own exam or choose from one of the several provided.
* Each exam may follow either standard timing (which what an actual exam will follow), custom timing (you decide), or be untimed (no limit).

As an example, here is what that means for the JEE Mains according to the pattern for 2022.

> | Section | Type | Number of questions | Marks if correct | Marks if wrong | Marks if unattempted |
> | -- | -- | -- | -- | -- | -- |
> | Physics MCQ | MCQ | 20 | +4 | -1 | 0 |
> | Physics Numeric | Numeric | 5 | +4 | 0 | 0 |
> | Chemistry MCQ | MCQ | 20 | +4 | -1 | 0 |
> | Chemistry Numeric | Numeric | 5 | +4 | 0 | 0 |
> | Mathematics MCQ | MCQ | 20 | +4 | -1 | 0 |
> | Mathematics Numeric | Numeric | 5 | +4 | 0 | 0 |
> 
> The test will be for 180 minutes (3 hours).

## Installation
1.  Clone the repository
2.  You must have a recent Python (3.10 or newer).
3.  Install the PyPi dependencies.

    ```sh
    python -m pip install -r requirements.txt
    ```

## Usage
1.  If you're running in a server deployment and will access the GUI over the network, create an environment variables file in the project root with the `JEE_PRAC_SERVER` variable set to `1`.

    ```sh
    echo "JEE_PRAC_SERVER=1" > .env
    ```
2.  Run with Python

    ```sh
    python app.py
    ```

    If you're running in a server, note that you might have to allow Python network access. Also note that, it might be a good idea to create a service in this case.

3.  A URI should be printed to the standard output. Copy and paste it into a web browser, and visit it.

4.  Proceed to setup and take the test from the GUI.

5.  Once your done with your test (or at any point when no exam is taking place but the script is running), you may append `/download` to the URI from step 3, and download your data as CSV files. It will always contain all the exams submitted so far.

## Test configuration
The first time you run this, it would create a folder `.jee-prac` in your home directory (on most Linux, MacOS, and PowerShell terminals, this is `~/.jee-prac`). This directory also has a JSON file called `preconfigured-exams.json`, which has data for some of the tests taken in India. You can modify this file with additional test patterns that would then appear in the GUI.

If you feel that you have added something significant, please feel free to submit a pull request with the modification applied to `data/preconfigured-exams.json`.
