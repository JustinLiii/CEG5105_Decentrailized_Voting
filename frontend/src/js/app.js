//import "../css/style.css"
const { blindSignRequest, getUserInfo } = require('./utils.js');
const { get_contract, getReadOnlyContract } = require('./contract.js');
require('dotenv').config();

async function vote () {
  console.log("vote")
  const { voterName, voterId } = getUserInfo()
  var candidateID = $("input[name='candidate']:checked").val();
  if (!candidateID) {
    $("#msg").html("<p>Please vote for a candidate.</p>")
    return
  }
  blindSignRequest(voterName, voterId, 'http://127.0.0.1:5000').then(function (privateKey) {
    get_contract(privateKey).then(function (instance) {
      instance.vote(parseInt(candidateID)).then(function (_) {
        $("#msg").html("<p>Voted</p>");
        window.location.reload(1);
      })
    }).catch(function (err) {
      console.error("ERROR! " + err.message)
    })
  })
}

function updateVoted() {
  getReadOnlyContract().then(function (contract) {
    contract.checkVote().then(function (voted) {
      console.log(voted);
      if (!voted) {
        $("#voteButton").attr("disabled", false);
        }
      }).catch(function (err) {
        console.error("ERROR! " + err.message)
      })
  })
}

window.App = {
  eventStart: function () {
    console.log("eventStart")

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

      VotingContract.checkVote().then(function (voted) {
        console.log(voted);
        if (!voted) {
          $("#voteButton").attr("disabled", false);
          }
        }).catch(function (err) {
          console.error("ERROR! " + err.message)
        })
    })
    updateVoted();
    $("#voteButton").click(vote); 
  }
}

window.App.eventStart()

console.log("App.js loaded")