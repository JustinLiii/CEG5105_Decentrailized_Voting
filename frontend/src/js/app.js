//import "../css/style.css"
const { getSignature, getSKForVoting, getUserInfo } = require('./utils.js');
const { get_contract, getReadOnlyContract } = require('./contract.js');
require('dotenv').config();

async function vote () {
  console.log("vote")
  var candidateID = $("input[name='candidate']:checked").val();
  if (!candidateID) {
    $("#msg").html("<p>Please vote for a candidate.</p>")
    return
  }
  getSKForVoting(window.user_hash,window.signature, 'http://127.0.0.1:5000').then(function (privateKey) {
    get_contract(privateKey).then(function (instance) {
      instance.vote(parseInt(candidateID)).then(function (_) {
        alert("Voted successfully");
        $("#msg").html("<p>Voted</p>");
        window.location.reload(1);
      })
    }).catch(function (err) {
      console.error("ERROR! " + err.message)
    })
  })
}

async function updateVoted() {
  fetch('http://127.0.0.1:5000/check_eligibility', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_hash: window.user_hash.toString(), signature: window.signature.toString() })
  }).then(function (response) {
    if (!response.ok) {
      console.error("ERROR! " + response.statusText)
      return
    }
    response.json().then(function (data) {
      var voted = !data.eligible
      if (voted) {
        // $("#msg").html("<p>Voted</p>")
        $("#voteButton").prop("disabled", true);
        $("#voteButton").html("Voted");
      } else {
        // $("#msg").html("<p>Not Voted</p>")
        $("#voteButton").prop("disabled", false);
        $("#voteButton").html("Vote");
      }
    })
  })
}

window.App = {
  eventStart: function () {
    console.log("eventStart")
    const { voterName, voterId } = getUserInfo()
    getSignature(voterName, voterId, 'http://127.0.0.1:5000').then(function ({message, signature}) {
      console.log(`message: ${message}, signature: ${signature}`);
      window.user_hash = message
      window.signature = signature
      updateVoted();
    });
    getReadOnlyContract().then(function (VotingContract) {
      VotingContract.getDates().then(function (result) {
        var startDate = new Date(Number(result[0]) * 1000);
        var endDate = new Date(Number(result[1]) * 1000);

        $("#dates").text(startDate.toDateString(("#DD#/#MM#/#YYYY#")) + " - " + endDate.toDateString("#DD#/#MM#/#YYYY#"));
      }).catch(function (err) {
        console.error("ERROR! " + err.message)
      });

      VotingContract.getCountCandidates().then(function (countCandidates) {
        for (var i = 0; i < countCandidates; i++) {
          VotingContract.getCandidate(i + 1).then(function (data) {
            var id = data[0];
            var name = data[1];
            var party = data[2];
            var voteCount = data[3];
            var viewCandidates = `<tr><td> <input class="form-check-input" type="radio" name="candidate" value="${id}" id=${id}>` + name + "</td><td>" + party + "</td><td>" + voteCount + "</td></tr>"
            $("#boxCandidate").append(viewCandidates)
          })
        }
        window.countCandidates = countCandidates
      });
    })
    $("#voteButton").click(vote); 
  }
}

window.App.eventStart()

console.log("App.js loaded")