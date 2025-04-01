const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");
// const Voting = artifacts.require("Voting");

describe("Voting", function () {
  // We define a fixture to reuse the same setup in every test.
  // We use loadFixture to run this setup once, snapshot that state,
  // and reset Hardhat Network to that snapshot in every test.
  async function candidateFixture() {
    const NAME = "Trump";
    const PARTY = "Republican";
    return { NAME, PARTY };
  }
  async function deployFixture() {

    const Voting = await hre.ethers.getContractFactory("Voting");
    const voting = await Voting.deploy();

    return { voting };
  }

  describe("Create candidate", function () {
    it("Should create a candidate", async function () {
      const { NAME, PARTY } = await loadFixture(
        candidateFixture
      );
      const { voting } = await loadFixture(
        deployFixture
      );
      await voting.addCandidate(NAME, PARTY);
      const candidateCount = await voting.getCountCandidates();
      expect(candidateCount).to.equal(1);
      const [cid, cname, cparty, voteCount] = await voting.getCandidate(1);
      
      expect(cname).to.equal(NAME);
      expect(cparty).to.equal(PARTY);
      expect(voteCount).to.equal(0);
    });
  });
});
