const express = require("express");
const app = express();
let cors = require("cors");

app.use(express.json());
app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*"); // update to match the domain you will make the request from
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  next();
});

/* let corsOptions = {
  origin: "*",
  methods: ["POST"],
  optionsSuccessStatus: 200, // some legacy browsers (IE11, various SmartTVs) choke on 204
  credentials: true,
  allowedHeaders: [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "device-remember-token",
    "Access-Control-Allow-Origin",
    "Origin",
    "Accept",
  ],
}; */

const port = process.env.PORT || 8000;

async function chatbot(findStr) {
  let { NlpManager } = require("node-nlp"); //natural language processing for chatbot

  const manager = new NlpManager({
    languages: ["en"],
    nlu: { useNoneFeature: false },
    nlu: { log: false },
    forceNER: true,
    ner: { useDuckling: false },
  });

  manager.addCorpus("./corpus.json");
  await manager.train();
  manager.save();
  // manager.load();

  const result = await manager.extractEntities("en", findStr);
  console.log(result);
  let response = await manager.process("en", findStr);
  // console.log(response);
  return response.answer;
}

app.post("/api/bot", (req, res, next) => {
  res.set("Content-Type", "application/json");

  chatbot(req.body.msg).then(async (response) => {
    if (response == null) {
      res.status(200).json({ message: "sorry I did not understand." });
    } else {
      res.status(200).json({ message: response });
    }
  });
});

app.listen(port, () => {
  console.log("Server app listening on port " + port);
});
