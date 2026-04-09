# Logo Installation Guide

## How to Add Your Logo

1. **Save your logo image** as `logo.png` in this folder:
   ```
   c:\Users\shalt\.vscode\ProgramFiles\EnergyTrack\static\images\logo.png
   ```

2. **Recommended Logo Specifications**:
   - Format: PNG (with transparent background)
   - Size: 512x512 pixels (or any square aspect ratio)
   - File name: `logo.png` (exactly)

3. **Where the Logo Appears**:
   - ✅ Landing page navbar (top left)
   - ✅ Dashboard sidebar (top center, 120px wide)
   - ✅ Login page (centered, 100px wide)
   - ✅ Register page (centered, 100px wide)
   - ✅ Admin login page (centered, 100px wide)
   - ✅ Browser favicon (tab icon)

4. **Alternative Formats**:
   If you want to use a different format, update the file paths in templates:
   - For JPG: Rename to `logo.jpg`
   - For SVG: Rename to `logo.svg`
   
   Then update all template references from:
   ```
   url_for('static', filename='images/logo.png')
   ```
   to:
   ```
   url_for('static', filename='images/logo.jpg')  # or logo.svg
   ```

## Quick Copy Command

If your logo is in Downloads or Desktop, use PowerShell:

```powershell
# From Downloads
Copy-Item "$env:USERPROFILE\Downloads\your-logo.png" "c:\Users\shalt\.vscode\ProgramFiles\EnergyTrack\static\images\logo.png"

# From Desktop
Copy-Item "$env:USERPROFILE\Desktop\your-logo.png" "c:\Users\shalt\.vscode\ProgramFiles\EnergyTrack\static\images\logo.png"
```

## Testing

After placing the logo:
1. Restart the Flask application
2. Visit http://127.0.0.1:5000
3. Check:
   - Landing page navbar (should show logo)
   - Login page (should show logo)
   - Dashboard sidebar (should show logo after login)
   - Browser tab (should show logo as favicon)

## Current Status

✅ All templates updated to use logo
✅ Static folder created
⏳ Waiting for logo.png file

---

**Note**: The logo from your attachment needs to be saved as a file in this directory.
