import {Given, Then, When} from "@cucumber/cucumber";

Given('there are {int} cucumbers', function (int) {
});

When('I eat {int} cucumbers', function (int) {
});

Then('I should have {int} cucumbers', function (int) {
    throw new Error("FAIL")
});
