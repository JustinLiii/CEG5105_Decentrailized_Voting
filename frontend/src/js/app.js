//import "../css/style.css"
require('dotenv').config();
const { ethers } = require("ethers");
const abi = [
  "function addCandidate(string,string) returns (uint256)",
  "function candidates(uint256) view returns (uint256, string, string, uint256)",
  "function checkVote() view returns (bool)",
  "function countCandidates() view returns (uint256)",
  "function getCandidate(uint256) view returns (uint256, string, string, uint256)",
  "function getCountCandidates() view returns (uint256)",
  "function getDates() view returns (uint256, uint256)",
  "function setDates(uint256,uint256)",
  "function vote(uint256)",
  "function voters(address) view returns (bool)",
  "function votingEnd() view returns (uint256)",
  "function votingStart() view returns (uint256)"
]
const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
window.App = {
  eventStart: function () {
    const signer = new ethers.Wallet("0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e", provider)
    VotingContract = new ethers.Contract(process.env.CONTRACT_ADDRESS, abi, signer);
    VotingContract.getCountCandidates().then(function (countCandidates) {
      $(document).ready(function () {
        $('#addCandidate').click(function () {
          var nameCandidate = $('#name').val();
          var partyCandidate = $('#party').val();
          VotingContract.addCandidate(nameCandidate, partyCandidate).then(function (result) { })

        });
        $('#addDate').click(function () {
          var startDate = Date.parse(document.getElementById("startDate").value) / 1000;

          var endDate = Date.parse(document.getElementById("endDate").value) / 1000;

          VotingContract.setDates(startDate, endDate).then(function (rslt) {
            console.log("tarihler verildi");
          });

        });

        VotingContract.getDates().then(function (result) {
          var startDate = new Date(result[0] * 1000);
          var endDate = new Date(result[1] * 1000);

          $("#dates").text(startDate.toDateString(("#DD#/#MM#/#YYYY#")) + " - " + endDate.toDateString("#DD#/#MM#/#YYYY#"));
        }).catch(function (err) {
          console.error("ERROR! " + err.message)
        });
      });

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
  },

  vote: function () {
    var candidateID = $("input[name='candidate']:checked").val();
    if (!candidateID) {
      $("#msg").html("<p>Please vote for a candidate.</p>")
      return
    }
    VotingContract.deployed().then(function (instance) {
      instance.vote(parseInt(candidateID)).then(function (result) {
        $("#voteButton").attr("disabled", true);
        $("#msg").html("<p>Voted</p>");
        window.location.reload(1);
      })
    }).catch(function (err) {
      console.error("ERROR! " + err.message)
    })
  }
}
