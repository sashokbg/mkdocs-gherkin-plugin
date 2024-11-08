# Feature: Content From Images

The PAM is able to classify a product and generate description for it based on one or more images.

Using multiple images from different angles allows the robot to "see" details that will normally be hidden.

Allowed image formats are:

- png
- jpeg

## Background:

* Given The user is logged-in

## Example: Uploading an image of a woman's jacket

* When an image of a woman's jacket is uploaded
* Then The product is classified as "Women's Jacket"

  ![Image](img/woman_jacket.png){width="256"}

## Example: Upload Images of Front and Lining of a Jacket

* Upload a black bomber jacket represented by two images.

  ![Bomber jacket 1](img/bomber.png){width=256}
  ![Bomber jacket 2](img/bomber_2.png){width=220}

* The second image shows the inner lining as orange.
* The robot will fill in the field "secondary color" as orange
