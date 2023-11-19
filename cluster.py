import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import csv
import graph2

def findJobTitle(user_skills):
    # Load the dataset
    df = pd.read_csv('cleaned_dataset.csv')
    user_skills = [word.lower() for word in user_skills]


    # Split the data into features (X) and labels (y)
    X = df['skill']
    y = df['category']

    # Convert text data to numerical features using CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the Decision Tree classifier
    clf = DecisionTreeClassifier()

    # Train the Decision Tree classifier
    clf.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = clf.predict(X_test)

    # Evaluate the accuracy of the model
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy * 100:.2f}%')



    # Now, you can use the trained model to predict the category for a user's input
    user_skills_transformed = vectorizer.transform(user_skills)
    user_category = clf.predict(user_skills_transformed)
    print(f"The predicted category for the user is: {user_category}")
    occur = {
        "Web" : 0,
        "Software Developer" : 0,
        "Ai" : 0
    }

    all_cat = []

# Open the CSV file
    with open('cleaned_dataset.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        # Loop through each row in the CSV
        for row in reader:
            # If the skill is in the list of skills
            if row['skill'] in user_skills:
                # Append the category to the list
                all_cat.append(row['category'])

    print(all_cat)

    for cat in all_cat:
        cat = cat.title()
        occur[cat] += 1

    maxwell = occur["Web"]
    maxnot = "Web"

    for occ, v in occur.items():
        if v > maxwell:
            maxnot = occ
            maxwell = v

    
    print(occur)

    print(f"The predicted category for the user is: {maxnot}")
    print(len(user_category))

    return maxnot

graph=[
    ("Software Engineer", 0),
    ("Web Developer", 1),
    ("Ai Engineer", 2)
]
start='Software Engineer'
# print(graph2.best_first_search(graph, start, "Web Developer"))