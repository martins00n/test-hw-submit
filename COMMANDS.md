I want to make a template repository for time series course.
We will have bunch of home works and projects.
Each homework and project will have its own folder.
Each folder will contain a README.md file with instructions and requirements.
And notebook to be filled by students.

Possible pipeline:

- we add homework notebook every week
- student make checkout of the repository
- student complete the homework in the notebook
- student submit the notebook for review as a pull request in their own fork of the repository
- some cells logging metrics and some data to json file
- ci system run some basic checks on the notebook that was submitted: it should run without errors, we compare logged metrics with expected ones
- if everything is ok we send mark to google file with students grades

this repeats every week for each homework

So set up the workflow for this repository for such 