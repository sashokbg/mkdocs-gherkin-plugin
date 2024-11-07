import {Given, Then, When} from "@cucumber/cucumber";
import fs from 'fs'

Given('there are {int} cucumbers', async function (int) {
    if (int == 12) {
        const stream = fs.createReadStream('./prince_of_persia.png');

        await this.attach(stream, { mediaType: 'image/png' });
    } else {
        const stream = fs.createReadStream('./prince_of_persia2.png');

        await this.attach(stream, { mediaType: 'image/png' });
    }
});

When('I eat {int} cucumbers', function (int) {
});

Then('I should have {int} cucumbers', function (int) {
    if (int == 7) {
        throw new Error("FAIL")
    }
});

Given('I work hard', function () {
});

When('The end of the month arrives', function () {
});

Then('I am payed well', function () {
    throw Error("")
});

