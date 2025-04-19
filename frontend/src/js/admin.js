const { get_contract } = require('./contract.js');

const privateKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

get_contract(privateKey).then(function (VotingContract) {
    $(document).ready(function () {
        $('#addCandidate').click(function () {
            var nameCandidate = $('#name').val();
            var partyCandidate = $('#party').val();
            VotingContract.addCandidate(nameCandidate, partyCandidate).then(function (_) {
                $('#name').val('');
                $('#party').val('');
                // pop up
                alert("Candidate added successfully");
                window.location.reload();
            });
        });
        $('#addDate').click(function () {   
            var startDate = Date.parse(document.getElementById("startDate").value) / 1000;

            var endDate = Date.parse(document.getElementById("endDate").value) / 1000;

            VotingContract.setDates(startDate, endDate).then(function (_) {
                document.getElementById("startDate").value = "";
                document.getElementById("endDate").value = "";
                // pop up
                alert("Election dates set successfully");
                window.location.reload();
            });
        });
    });
});