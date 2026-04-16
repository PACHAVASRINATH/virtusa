function calculate() {
  let km = Number(document.getElementById("km").value);
  let vehicle = document.getElementById("vehicle").value;
  let hour = Number(document.getElementById("hour").value);

  let rates = {
    Economy: 10,
    Premium: 18,
    SUV: 25
  };

  let fare = km * rates[vehicle];

  if (hour >= 17 && hour <= 20) {
    fare *= 1.5;
  }

  document.getElementById("result").innerText = "Fare: ₹" + fare;
}