//import "../css/style.css"
const { ethers } = require("ethers");
const contract_info = require('../../deployed.json')
const fs = require('fs').promises;
const { blind, unblind, verify } = require('./blind_sign.js');

let VotingContract = null; // Don't use this, use get_contract

async function blindSignRequest(userName, userId, serverUrl) {
  // 用户信息
  const userInfo = { id_number: userId, name: userName };

  // 步骤1：获取并解析公钥
  const pubResp = await fetch('/public.pem');
  if (!pubResp.ok) {
    throw new Error(`无法加载公钥文件: ${pubResp.statusText}`);
  }
  const pem = await pubResp.text();
  const pubKey = window.forge.pki.publicKeyFromPem(pem);

  // 步骤2：对用户信息进行 SHA-256 哈希
  const sortedJson = JSON.stringify(userInfo, Object.keys(userInfo).sort());
  const encoder = new TextEncoder();
  const data = encoder.encode(sortedJson);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  const message = BigInt('0x' + hashHex);

  // 步骤3：盲化消息
  const { blinded: blindedMsg, r } = blind({
    key: pubKey,
    message
  });

  // 步骤4：向服务器请求盲签名
  const signResp = await fetch(`${serverUrl}/blind_sign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ blinded_message: blindedMsg.toString() })
  });
  if (!signResp.ok) {
    throw new Error(`盲签名请求失败: ${signResp.statusText}`);
  }
  const { blind_signature } = await signResp.json();
  const blindedSignature = BigInt(blind_signature);

  // 步骤5：解盲签名
  const signature = unblind({
    key: pubKey,
    signed: blindedSignature,
    blind: r
  });

  // 步骤6：验证签名
  const isValid = verify({
    key: pubKey,
    message,
    signature
  });
  if (!isValid) {
    throw new Error('签名验证失败！');
  }
  console.log('签名验证成功！');

  // 步骤7：请求分配匿名账户
  const accountResp = await fetch(`${serverUrl}/assign_account`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_info: userInfo, signature: signature.toString() })
  });
  if (!accountResp.ok) {
    const errText = await accountResp.text();
    throw new Error(`请求分配账户失败: ${errText}`);
  }
  const { account_address } = await accountResp.json();
  console.log(`成功获取匿名账户: ${account_address}`);

  return account_address;
}

async function get_contract(userName, userId) {
  if (VotingContract != null) {
    return VotingContract;
  }
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
  const privateKey = await blindSignRequest(userName, userId, 'http://127.0.0.1:5000')
  const signer = new ethers.Wallet(privateKey, provider)
  VotingContract = new ethers.Contract(contract_info.contracts.Voting.address, contract_info.contracts.Voting.abi, signer); 
  return VotingContract 
}

window.App = {
  eventStart: function () {
    get_contract('qwq', '114514').then(function (VotingContract) {
      VotingContract.getCountCandidates().then(function (countCandidates) {
        $(document).ready(function () {
          $('#addCandidate').click(function () {
            var nameCandidate = $('#name').val();
            var partyCandidate = $('#party').val();
            VotingContract.addCandidate(nameCandidate, partyCandidate);
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
    })

  },
  vote: function () {
    var candidateID = $("input[name='candidate']:checked").val();
    if (!candidateID) {
      $("#msg").html("<p>Please vote for a candidate.</p>")
      return
    }
    get_contract('qwq','114514').then(function (instance) {
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
