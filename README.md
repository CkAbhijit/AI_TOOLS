# Multi-Tools Website

A fully responsive website containing 100+ free online tools including image converters, calculators, SEO tools, text utilities, unit converters, developer tools, and more. Built with HTML, CSS (Bootstrap), and vanilla JavaScript.

## Features

- 100+ free online tools organized by categories
- Responsive design that works on desktop, tablet, and mobile devices
- Search functionality to find tools quickly
- Modern and attractive UI with Bootstrap
- No external JavaScript frameworks required
- Dynamic header and footer loading
- Favorites and recent tools tracking using localStorage

## Project Structure

```
multi-tools/
├── css/
│   └── style.css
├── js/
│   ├── common.js
│   ├── index.js
│   └── tools-data.js
├── tools/
│   ├── image-tools/
│   ├── seo-tools/
│   ├── text-tools/
│   ├── developer-tools/
│   ├── calculators/
│   ├── unit-converters/
│   ├── security-tools/
│   ├── social-media-tools/
│   └── miscellaneous/
├── images/
├── header.html
├── footer.html
├── index.html
└── README.md
```

## How to Run

### Option 1: Using Python's built-in HTTP server

1. Make sure you have Python installed on your computer
2. Open a terminal/command prompt
3. Navigate to the project directory
4. Run one of the following commands:

   For Python 3:
   ```
   python -m http.server 8000
   ```
   
   For Python 2:
   ```
   python -m SimpleHTTPServer 8000
   ```

5. Open your web browser and go to: `http://localhost:8000`

### Option 2: Using Node.js and http-server

1. Make sure you have Node.js installed on your computer
2. Install http-server globally:
   ```
   npm install -g http-server
   ```
3. Navigate to the project directory in the terminal
4. Run:
   ```
   http-server -p 8000
   ```
5. Open your web browser and go to: `http://localhost:8000`

### Option 3: Using Visual Studio Code Live Server

1. Install Visual Studio Code
2. Install the "Live Server" extension by Ritwick Dey
3. Open the project folder in VS Code
4. Right-click on `index.html` and select "Open with Live Server"
5. The website will automatically open in your default browser

## Adding New Tools

To add a new tool:

1. Create a new HTML file in the appropriate category folder under `tools/`
2. Use the existing tool templates as a reference
3. Add the tool information to the `toolsData` object in `js/tools-data.js`

## Monetization

The website includes designated ad spaces that can be used with:

- Google AdSense
- Affiliate marketing links
- Direct advertising

## License

This project is available for personal and commercial use.

## Contact

For questions or support, please contact: contact@multi-tools.com 