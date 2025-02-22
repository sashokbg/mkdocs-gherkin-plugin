module.exports = {
    default: {
        format: ['message:reports/gherkin_messages.ndjson'],
        require: ['steps/**/*.js'],
        paths: ['../docs/**/*.feature.md']
    },
};

