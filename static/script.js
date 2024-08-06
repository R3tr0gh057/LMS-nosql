document.addEventListener("DOMContentLoaded", function () {
  const startReadButton = document.getElementById("startRead");
  const serialSelectBtn = document.getElementById("SerialSelector");
  const keystrokeToggleButton = document.getElementById("keystrokeToggle");
  const stopReadButton = document.getElementById("stopRead");
  const haltReadButton = document.getElementById("stopReading");
  // const startWriteButton = document.getElementById("startWrite");
  const writeDataButton = document.getElementById("writeData");
  const stopWriteButton = document.getElementById("stopWrite");
  const container = document.getElementById("container");

  let status = false;

  // Universal function to fetch endpoints
  async function sendCommand(url) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const result = await response.json();
      console.log(result.status);
    } catch (error) {
      console.error("Error:", error);
    }
  }

  // Serial port selector
  serialSelectBtn.addEventListener("click", (event) => {
    event.preventDefault();
    connectSerialPort();
  });

  startReadButton.addEventListener("click", async (event) => {
    event.preventDefault();

    if (status) {
      // Fetching the read trigger
      sendCommand("/startRead");
      // Delay to mitigate serial conflict
      await new Promise((r) => setTimeout(r, 500));

      // CSS for transition
      startReadButton.classList.add("active");
      startReadButton.textContent = "Keystrokes active . . .";

      // Fetching the keystroke trigger
      const url = "/keystrokeMode/" + encodeURIComponent(status ? 1 : 0);
      console.log("Sent " + url);
      sendCommand(url);
    } else {
      sendCommand("/startRead");
      // CSS for transition
      startReadButton.classList.add("active");
      startReadButton.textContent = "Reading Data . . .";
    }
  });

  stopReadButton.addEventListener("click", async (event) => {
    event.preventDefault();
    // CSS change for start reading button
    startReadButton.classList.remove("active");
    startReadButton.textContent = "Start Reading";

    // CSS for transition
    container.classList.add("active");

    sendCommand("/stopRead");
    // Delay to mitigate serial conflict
    await new Promise((r) => setTimeout(r, 500));
    // Send the second command to start the write function
    sendCommand("/startWrite");
  });

  // // Removed start write binding and changed it to auto write
  // startWriteButton.addEventListener("click", (event) => {
  //   event.preventDefault();
  //   sendCommand("/startWrite");
  // });

  // Stop reading endpoint call
  haltReadButton.addEventListener("click", async (event) => {
    event.preventDefault();
    sendCommand("/stopRead");

    // Delay to mitigate serial conflict
    await new Promise(r => setTimeout(r, 500));

    // Stop keystrokes if running
    if (status) keystrokeToggleButton.click();

    // CSS change for start reading button
    startReadButton.classList.remove("active");
    startReadButton.textContent = "Start Reading";
  });

  // Stop writing endpoint call
  stopWriteButton.addEventListener("click", (event) => {
    event.preventDefault();
    sendCommand("/stopWrite");

    // CSS for transition
    container.classList.remove("active");

    // Clear old values
    document.getElementById("newData").value = "";
  });

  // Write data endpoint call
  writeDataButton.addEventListener("click", async function (event) {
    event.preventDefault();
    const data = document.getElementById("newData").value;
    const url = "/newWrite/" + encodeURIComponent(data);
    await sendCommand(url);
    window.alert("Data modified");
  });

  // Keystroke toggle endpoint call
  keystrokeToggleButton.addEventListener("click", () => {
    status = !status;
    console.log("Keystroke status: " + status)
  });

  // Update read data function call
  async function getReadData() {
    try {
      const response = await fetch("/getReadData");
      const result = await response.json();
      if (result.uid == "PCD_Authenticate() failed: Error in communication." || result.uid == "PCD_Authenticate() failed: Timeout in communication." || result.uid == "MIFARE_Read() failed: The CRC_A does not match.") {
        document.getElementById("cardUID").value = "Try again";
        await sendCommand("/startRead");
      }
      else {
        document.getElementById("cardUID").value = result.uid;
        document.getElementById("cardData").value = result.data;
      }

    } catch (error) {
      console.error("Error fetching read data:", error);
    }
  }

  function loadPorts() {
    fetch('/ports')
      .then(response => response.json())
      .then(data => {
        const portSelect = document.getElementById('port');
        portSelect.innerHTML = '';
        data.ports.forEach(port => {
          const option = document.createElement('option');
          option.value = port;
          option.text = port;
          portSelect.appendChild(option);
        });
      })
      .catch(error => {
        console.error('Error fetching ports:', error);
      });
  }

  function connectSerialPort() {
    const selectedPort = document.getElementById('port').value;
    fetch('/connect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ port: selectedPort }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // enable the buttons once the listener is established
          document.getElementById("writeData").disabled = false;
          document.getElementById("keystrokeToggle").disabled = false;
          document.getElementById("startRead").disabled = false;
          document.getElementById("stopReading").disabled = false;

          alert('Connected to ' + selectedPort);
        } else {
          alert('Failed to connect: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

  loadPorts()
  setInterval(getReadData, 500);

  // // Sending command to start reading at startup
  // sendCommand("/startRead");
});
