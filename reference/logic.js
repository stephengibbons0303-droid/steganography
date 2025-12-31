/* STEGANOGRAPHY program
       * Hides one 8-bit color image called "hide" in another 8-bit image called "start". 
       * New combined 8-bit color image will look like the “start” image. 
       * First few bits of each color (R,G,B) binary value of each pixel of this 
       * new combined image are used to keep information about “start” image, 
       * last few bits are used for “hide” image. So, first bits of the image hide 
       * become last bits of the combined image. 
       * User can choose how many bits to use to hide an image changing the value 
       * of the variable bitsHide in the section PARAMETER VALUES SET BY USER. 
       * The program also includes:
       * - function to crop images to the smallest width and height of both images 
       * - function to extract hidden image from the combined image
       * After assigning the images start and hide, and running the program, 
       * it prints out the combined and extracted images. 
       */

      //========= PARAMETER VALUES SET BY USER =========//
      var bitsHide = 2;  /* set the number of bits out of 8 to hide an image in, 
          it should be WITHIN THE RANGE FROM 1 TO 7. */
      var start = new SimpleImage("Eva.jpg");  /* assign start image to hide 
          another image in it */
      var hide = new SimpleImage("text.jpg");  // assign image to hide 

      //============= CALCULATED ARGUMENTS =============//
      var factorChop = Math.pow(2, bitsHide);  /* factor based on the number of bits 
          to be left for the image start in which another image is hidden */
      var factorHide = Math.pow(2, 8-bitsHide);  /* factor for the hidden image based 
          on the number of bits to be used to hide this image */ 
      //================================================//

      function pixchange(pixval){
          /* Reduces an argument to the nearest down value divisible by factorChop
           * without a remainder. "Extra" values are thrown away by floor division
           * of the argument by var factorChop (remainder is truncated). The result
           * is multiplied by the same var factorChop. This is the equivalent of making
           * last bits of 8-bit binary argument's value equal to 0, the number of these
           * bits is defined by var bitsHide.
           */ 
          var x = Math.floor(pixval/factorChop) * factorChop;
          return x;
      }
      function chop2hide(image) { 
          /* Chops each pixel color value of an image to make last bits of its 8-bit
           * binary value equial to 0 via reducing its decimal value to the nearest
           * down value divisible by factorChop, function pixchange is called for that
           */
          for(var px of image.values()){
              px.setRed(pixchange(px.getRed()));
              px.setGreen(pixchange(px.getGreen()));
              px.setBlue(pixchange(px.getBlue()));
          }
          return image;
      }
      function shift(im) {
          /* Shifts every pixel color value to make first bits of its 8-bit binary value
           * equial to 0 through its decimal value floor division by var factorHide, 
           * number of these bits is equal to the difference "8 - bitsHide". 
           */
          var nim = new SimpleImage(im.getWidth(), 
                                      im.getHeight());
          for(var px of im.values()){
              var x = px.getX();
              var y = px.getY();
              var npx = nim.getPixel(x,y);
              npx.setRed(Math.floor(px.getRed()/factorHide));
              npx.setGreen(Math.floor(px.getGreen()/factorHide));
              npx.setBlue(Math.floor(px.getBlue()/factorHide));
          }
          return nim;
      }

      function widthCrop(image1, image2) {
          // returns the smallest width of two images
          if (image1.getWidth() <= image2.getWidth()) {
              return(image1.getWidth());
          }
          else {
              return(image2.getWidth());
          }
      }

      function heightCrop(image1, image2) {
          // returns the smallest height of two images
          if (image1.getHeight() <= image2.getHeight()) {
              return(image1.getHeight());
          }
          else {
              return(image2.getHeight());
          }
      }

      // define and set the smallest width of two images
      var cropWidth = widthCrop(start, hide);
      // define and set the smallest height of two images
      var cropHeight = heightCrop(start, hide);

      function crop(image, width, height) {
          // crops image to the width and height passed to the function
          var cropImage = new SimpleImage(cropWidth, cropHeight);
          for (var pixel of cropImage.values()) {
              var x = pixel.getX();
              var y = pixel.getY();
              var inPixel = image.getPixel(x, y);
              pixel.setAllFrom(inPixel);
          }
          return cropImage;
      }

      var startCrop = crop(start, cropWidth, cropHeight);  /* create cropped copy of 
          "start" image through calling function "crop" */ 

      var startChop = chop2hide(start);  /* create color values chopped version of 
          "startCrop" image through calling function "chop2hide" */

      var hideCrop = crop(hide, cropWidth, cropHeight); /* create cropped copy of
          "hide" image through calling function "crop" */  
          
      var hideShift = shift(hideCrop);  /* create new version of "hideCrop" image 
          with "shifted" color values through calling function "shift" */

      function newpv(p, q) {
          // adds two arguments and returns the sum if it's not more than 255
          if (p + q > 255) {
              return("error: pixel value > 255");
          }
          else {
              return(p + q);
          }
      }

      function combine(image1, image2) {
          /* Sets the value of every color of every pixel of resulting combined image
           * to the sum of the corresponding pixel values of image1 and image2. 
           * Returns this combined image. 
           */
          var combiImg = new SimpleImage(cropWidth, cropHeight);
          for (var px of combiImg.values()) {
              var x = px.getX();
              var y = px.getY();
              var px1 = image1.getPixel(x, y);
              var px2 = image2.getPixel(x, y);
              combiImg.setRed(x, y, newpv(px1.getRed(), px2.getRed()));
              combiImg.setGreen(x, y, newpv(px1.getGreen(), px2.getGreen()));
              combiImg.setBlue(x, y, newpv(px1.getBlue(), px2.getBlue()));
          }
          return combiImg;
      }

      var combinedImg = combine(startChop, hideShift);  // create combined output image

      /* TEST the resulting image by sampling a pixel that is in image1, image2 and 
       * the new image and check their RGB values to see if the sum is correct. 
       */
      print("combinedImg");
      print(combinedImg);
      print("startChop", startChop.getRed(50, 50), startChop.getGreen(50, 50), 
                          startChop.getBlue(50, 50));
      print("hideShift", hideShift.getRed(50, 50), hideShift.getGreen(50, 50), 
                          hideShift.getBlue(50, 50));
      print("combinedImg", combinedImg.getRed(50, 50), combinedImg.getGreen(50, 50),
                          combinedImg.getBlue(50, 50));
      print("");

      function extract(image) {
          /* Extracts hidden image from the visible combined image containing hidden image.
           * Each color value of each pixel of the combined image is modulo divided by 
           * var factorChop to find the remainder of such division. This is the equivalent
           * of getting only last bits of 8-bit binary color value, number of these bits 
           * is defined by var bitsHide via var factorChop. The remainder is multiplied 
           * by var factorHide, this operation is opposite to executed by function shift.
           */
          var extractImg = new SimpleImage(cropWidth, cropHeight);
          for (var px of image.values()) {
              var x = px.getX();
              var y = px.getY();
              var npx = extractImg.getPixel(x,y);
              npx.setRed((px.getRed() % factorChop) * factorHide);
              npx.setGreen((px.getGreen() % factorChop) * factorHide);
              npx.setBlue((px.getBlue() % factorChop) * factorHide);
          }
          return extractImg;
      }

      extractImg = extract(combinedImg);  /* re-assign and get output extracted 
          * hidden image extractImg through calling function extract with the image 
          * combinedImg as an argument 
          */ 
          
      print("extractImg");
      print(extractImg);
      /* TEST the result of hidden image extraction via printing and comparing 
       * RGB values of the hidden and extracted images, extracted image RGB values
       * should be hidden image RGB values multiplied by factorHide */
      //print(npxRed);
      print("hideShift", hideShift.getRed(50, 50), hideShift.getGreen(50, 50), 
                          hideShift.getBlue(50, 50)); 
      print("extractImg", extractImg.getRed(50, 50), 
          extractImg.getGreen(50, 50), extractImg.getBlue(50, 50));
