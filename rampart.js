#!/usr/bin/env node

const server = require("./server/server");
const { parser } = require("./server/args");
const { getInitialConfig} = require("./server/config/getInitialConfig");
const startUp = require("./server/startUp");
const { startBasecalledFilesWatcher } = require("./server/watchBasecalledFiles");
const Datastore = require("./server/datastore").default;
const { fatal, trace } = require('./server/utils');
const { setUpPipelines } = require("./server/config/pipeline");

const main = async () => {
    try {
        const args = parser.parseArgs();
        if (args.verbose) global.VERBOSE = true;
        
        const {config, pathCascade} = getInitialConfig(args);
        global.config = config;
        global.datastore = new Datastore();
        global.pipelineRunners = setUpPipelines(config, args, pathCascade);
        global.filesSeen = new Set(); /* files (basenames) seen (FASTQ or CSV) */
        server.run({devClient: args.devClient, ports: args.ports});

        if (global.config.run.clearAnnotated) {
          await startUp.removeExistingAnnotatedCSVs();
        } else {
          await startUp.processExistingAnnotatedCSVs();
        }
        await startBasecalledFilesWatcher();

    } catch (err) {
        trace(err);
        fatal(`Fatal error: ${err.message}`);
    }
};

main();
