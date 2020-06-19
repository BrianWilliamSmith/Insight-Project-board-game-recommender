from classifier import classify_stuff
from recommender import recommend_stuff

image = load_image()

image_label = classify_stuff(image)
recommendation = recommend_stuff(image_label)

print(image_label, recommendation)