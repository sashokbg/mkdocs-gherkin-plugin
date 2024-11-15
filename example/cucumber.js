module.exports = {
    default: {
        format: ['message:gherkin_messages.ndjson'],
        require: ['steps/**/*.js'],
        paths: ['docs/**/*.feature.md']
    },
};

