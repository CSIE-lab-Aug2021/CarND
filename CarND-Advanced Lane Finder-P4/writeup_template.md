

##**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

###File included in this submission
The following files have been included in this submission
* Ipython notebook with the code - P4_advanced_lane_detection_final.ipynb
* Folder with output images
* Ouput video with lane lines identified
* This write up file


[//]: # (Image References)

[image1]: ./output_images/orig_camera_img.png "Undistorted Camera"
[image2]: ./test_images/test1.jpg "Road Transformed"
[image3]: ./examples/binary_combo_example.jpg "Binary Example"
[image4]: ./examples/warped_straight_lines.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
###Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
###Writeup / README

####1. Provide a Writeup / README that includes all the rubric points and how you addressed each one. 

You're reading it!
###Camera Calibration

####1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in the code cell **2** of the IPython notebook located in " P4_advanced_lane_detection_final.ipynb" 

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image. This example has 9x6 chessboard corners. Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

<img src="./output_images/orig_camera_img.png" width="600">

###Pipeline (single images)

####2. Apply distortion correction to test images
I pickled the camera calibration coefficients mtx and dst (code line **3**) and used these in cv2.undistort (code line **5**) to remove distortion in the test images. See example below of a distortion corrected image
<img src="./output_images/undist_test_image.png" width="600">

####3. Create a thresholded binary image
I used a combination of color and gradient thresholds to generate a binary image (The code for doing various thresholding operations is in cell **5** and the parameters chosen for these functions are in code line **7**). I found that gradient thresholding using sobel operator in x-direction was the most effective. For color thresholding I used the s-channel to identify yellow and white lines better under different lightening conditions. Further I combined sobelx gradient thresholding and s- color thresholds to obtain the thresholded binary image. The parameters for these operators were chosen by trial and error. See below the result of these operations:

<img src="./output_images/threshold_binary.png" width="600">

####4. Perspective transform
After the thresholding operation, I performed perspective transform to change the image to bird's eye view. This is done because we can use this to identify the curvature of the lane and fit a polynomial to it. To perform the perspective transform, I identified 4 src points that form a trapezoid on the image and 4 dst points such that lane lines are parallel to each other after the transformation. The dst points were chosen by trial and error but once chosen works well for all images and the video since the camera is mounted in a fixed position. Finally I used the cv2.getPerspective to identify M and then cv2.warpPerspective to use the M matrix to warp an image. The code for warp function is in code cell **5** 

The following source and destination points were chosen:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 800, 510      | 650, 470      | 
| 1150, 700     | 640, 700      |
| 270, 700      | 270, 700      |
| 510, 510      | 270, 510      |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.
<img src="./output_images/warped1.PMG" width="600">

####5.Identify lane-line pixels and fit their positions with a polynomial

Then I did some other stuff and fit my lane lines with a 2nd order polynomial kinda like this:

![alt text][image5]

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in lines # through # in my code in `my_other_file.py`

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines # through # in my code in `yet_another_file.py` in the function `map_lane()`.  Here is an example of my result on a test image:

![alt text][image6]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./project_video.mp4)

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  
