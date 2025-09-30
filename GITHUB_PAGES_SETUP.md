# 🚀 GitHub Pages Setup Guide

This guide will help you set up your Hand Gesture Communication App landing page on GitHub Pages with working video demos.

## 📋 Prerequisites

- GitHub account
- Your project repository on GitHub
- Video files from your `media/` folder

## 🎬 Step 1: Upload Videos to GitHub

### Option A: Using GitHub Web Interface

1. **Go to your repository** on GitHub
2. **Navigate to the root directory**
3. **Create a new folder** called `media` (if it doesn't exist)
4. **Upload your videos**:
   - `concatenated_video.mp4`
   - `hand gesture.mp4`
   - `video1.mp4`
   - `video2.mp4`
   - `video3.mp4`
   - `video4.mp4`

### Option B: Using Git Commands

```bash
# Navigate to your project directory
cd Hand-Gesture-Project

# Add the media folder to git
git add media/

# Commit the changes
git commit -m "Add demo videos for GitHub Pages"

# Push to GitHub
git push origin main
```

## 🌐 Step 2: Enable GitHub Pages

1. **Go to your repository** on GitHub
2. **Click on "Settings"** tab
3. **Scroll down to "Pages"** section
4. **Under "Source"**, select **"Deploy from a branch"**
5. **Select "main" branch** and **"/ (root)"** folder
6. **Click "Save"**

## 🔗 Step 3: Update Video URLs

After uploading videos, update the video URLs in `index.html`:

```html
<!-- Replace these URLs with your actual GitHub repository URLs -->
<source src="https://raw.githubusercontent.com/YOUR_USERNAME/Hand-Gesture-Project/main/media/concatenated_video.mp4" type="video/mp4">
<source src="https://raw.githubusercontent.com/YOUR_USERNAME/Hand-Gesture-Project/main/media/hand%20gesture.mp4" type="video/mp4">
<source src="https://raw.githubusercontent.com/YOUR_USERNAME/Hand-Gesture-Project/main/media/video1.mp4" type="video/mp4">
<source src="https://raw.githubusercontent.com/YOUR_USERNAME/Hand-Gesture-Project/main/media/video2.mp4" type="video/mp4">
```

## 🎯 Step 4: Update Repository URLs

Update all GitHub links in `index.html`:

```html
<!-- Replace YOUR_USERNAME with your actual GitHub username -->
<a href="https://github.com/YOUR_USERNAME/Hand-Gesture-Project" target="_blank">
<a href="https://github.com/YOUR_USERNAME/Hand-Gesture-Project/issues" target="_blank">
<a href="https://github.com/YOUR_USERNAME/Hand-Gesture-Project/discussions" target="_blank">
```

## 🚀 Step 5: Deploy

1. **Commit and push** your changes:
   ```bash
   git add .
   git commit -m "Update landing page with correct URLs"
   git push origin main
   ```

2. **Wait 5-10 minutes** for GitHub Pages to build

3. **Visit your site** at: `https://YOUR_USERNAME.github.io/Hand-Gesture-Project/`

## 🎬 Video Requirements

### Recommended Video Specifications:
- **Format**: MP4 (H.264 codec)
- **Resolution**: 720p or 1080p
- **Duration**: 10-30 seconds for demo videos
- **File Size**: Under 10MB each (for faster loading)
- **Aspect Ratio**: 16:9 for best display

### Video Content Suggestions:
- **concatenated_video.mp4**: Show text-to-sign conversion result
- **hand gesture.mp4**: Show gesture recognition in action
- **video1.mp4**: Show individual sign language gestures
- **video2.mp4**: Show voice-to-sign conversion result

## 🔧 Troubleshooting

### Videos Not Loading?
1. **Check file names** - ensure they match exactly (including spaces)
2. **Check file size** - GitHub has a 100MB limit per file
3. **Check URL encoding** - spaces in filenames need to be `%20`
4. **Wait for propagation** - changes can take 5-10 minutes

### GitHub Pages Not Updating?
1. **Check build status** in the "Actions" tab
2. **Ensure index.html** is in the root directory
3. **Check branch settings** in Pages configuration
4. **Clear browser cache** and try again

## 📱 Testing

Test your landing page on:
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile devices (iOS Safari, Android Chrome)
- ✅ Different screen sizes
- ✅ Video playback functionality

## 🎉 Final Result

Your landing page will showcase:
- ✅ **Real demo videos** from your app
- ✅ **Interactive interface** mockups
- ✅ **Communication flow** visualization
- ✅ **Technology stack** display
- ✅ **Professional design** with working videos

## 📞 Support

If you encounter issues:
1. Check GitHub Pages documentation
2. Verify file permissions and names
3. Test video URLs directly in browser
4. Check browser console for errors

---

**Your Hand Gesture Communication App landing page is now ready to impress visitors with real working demos!** 🚀
