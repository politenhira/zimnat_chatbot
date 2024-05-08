function sendMessage(message, itsMe) {
  // ...Mario
  var messageList = document.getElementById("message-list");

  var scrollToBottom =
    messageList.scrollHeight -
      messageList.scrollTop -
      messageList.clientHeight <
    80;

  var lastMessage = messageList.children[messageList.children.length - 1];

  var newMessage = document.createElement("span");
  newMessage.innerHTML = message;

  var className;

  if (itsMe) {
    className = "me";
    scrollToBottom = true;
  } else {
    className = "not-me";
  }

  if (lastMessage && lastMessage.classList.contains(className)) {
    lastMessage.appendChild(document.createElement("br"));
    lastMessage.appendChild(newMessage);
  } else {
    var messageBlock = document.createElement("div");
    messageBlock.classList.add(className);
    messageBlock.appendChild(newMessage);
    messageList.appendChild(messageBlock);
  }

  if (scrollToBottom) messageList.scrollTop = messageList.scrollHeight;
}

var message = document.getElementById("message-input");
message.addEventListener("keypress", function (event) {
  var key = event.which || event.keyCode;
  if (key === 13 && this.value.trim() !== "") {
    sendMessage(this.value, true);
    talkToSuki(this.value);
    this.value = "";
  }
});

sendMessage("Hey!", false);
sendMessage("How are you doing?", false);
sendMessage("My name is Suki, your Zimnat assistant, Do you have an account with us?", false);
showSuggessions(["Yes, I have an account", "I don't have one", "I just want to enquire about Zimnat services"])

function talkToSuki(inputValue) {
  // Data to send in the POST request
  const postData = {
    input: inputValue,
  };

  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(postData),
  };
  let indicator = document.getElementById("indicator");
  indicator.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;Typing ...";
  fetch("/hey/suki", options)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
       indicator.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;Online";
      sendMessage(data.response, false);
    })
    .catch((error) => {
      console.log(error);
       indicator.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;Online";
      sendMessage( "Sorry I am not available now, please check back some time.🥹", false);
    });
}

function showSuggessions(suggessions) {
  var messageList = document.getElementById("message-list");
  var lastMessage = messageList.children[messageList.children.length - 1];
  let pillContainer = document.createElement("div");
  pillContainer.classList.add("pill-container");
  //
  suggessions.forEach(text => {
    let pill = document.createElement("span");
    pill.classList.add("badge");
    pill.classList.add("bg-secondary-soft");
    pill.innerHTML = text;
    pill.addEventListener("click", () => {
      sendMessage(text.trim(), true);
      talkToSuki(text.trim())
    });
    pillContainer.appendChild(pill);


  });
  lastMessage.insertAdjacentElement("afterend", pillContainer);
}

// close button and clear the chatbot session
const closeBtn = document.getElementsByClassName("close-button")[0];
closeBtn.addEventListener("click", () => {
//   make a get request to /hey/suki
  fetch("/hey/suki/clear", {
    method: "GET"
  }).then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }else{
       var messageList = document.getElementById("message-list");
       messageList.innerHTML = "";
       sendMessage("My name is Suki, your Zimnat assistant, Do you have an account with us?", false);
       showSuggessions(["Yes, I have an account", "I don't have one", "I just want to enquire about Zimnat services"])
    }
  })
});


// : upload document
document.getElementById("document-picker").addEventListener("click", () => {
  document.getElementById("file").click();
});

document.getElementById("file").addEventListener("change", (e) => {
  const file = e.target.files[0];
  const fileSizeInMB = file.size / (1024 * 1024); // Convert bytes to MB
  console.log(file);

  if (fileSizeInMB > 10) {
    sendMessage("Sorry, File size exceeds 10MB limit. Please choose a smaller file.", false)
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const options = {
    method: "POST",
    headers: {
      // No need to set Content-Type, fetch sets it automatically for FormData
    },
    body: formData,
  };
  sendMessage(`${file.name} - ${fileSizeInMB.toFixed(2)}mb`, true)
  fetch("suki/upload", options)
    .then((response) => {
      if (!response.ok) {
        sendMessage("Error connecting to nework", false)
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      sendMessage(data.message, false)
    })
    .catch((error) => {
      console.log(error);
      sendMessage("Ouch, an error occured while processing your request", false)
    });
});



