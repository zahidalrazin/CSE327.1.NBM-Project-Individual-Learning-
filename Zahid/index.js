
import express from "express";
const app = express();
const port = 3000;

app.get("/", (req, res) => { 
    res.send("<h1>Hello</h1>")
});

app.get("/contact", (req, res) => {
    res.send("<h1>Contact:</h1><p>01970297852</p>");
})

app.get("/about", (req, res) => {
    res.send("<h1>About me: </h1><p>I am a full stack web developer</p>");
})

app.listen(port, () => {
    console.log(`Surver running on port ${port}`);
});

// import express from "express";
// const app = express();
// const port = 3000;

// app.get("/", (req, res) => {
//     res.send("<h1>Hello</h1>")
// });

// app.get("/contact", (req, res) => {
//     res.send("<h1>Contact</h1><p>Phone: 01970297852</p>");
// });

// app.get("/about", (req, res) =>{
//     res.send("<h1>About Me</h1><p>Hi, i am Zahid a Full Stack Web Developer.</p>");
// } );

// app.listen(port, () => {
//     console.log(`Surver running on port ${port}`);
// });





