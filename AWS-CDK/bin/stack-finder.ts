#!/usr/bin/env node
import 'source-map-support/register';
import cdk = require('@aws-cdk/core');
import { WebService } from '../lib/stack-finder-webservice';
import { App, Stack, StackProps, Tags } from '@aws-cdk/core';


class StackFinderStack extends Stack {
    constructor(scope: App, id: string, props?: StackProps) {
        super(scope, id, props);
        
        new WebService(this, 'webservice-stack-finder', {
            repository: "ardis/stack_finder",
            tag: "1."+String(process.env.TAG),
            memoryLimitMiB: 2048,
            cpu: 1024,
            container_env: {
                AWS_S3_ACCESS_KEY: process.env.STACK_FINDER_AWS_ACCESS_KEY,
                AWS_S3_SECRET_KEY: process.env.STACK_FINDER_AWS_SECRET_KEY,
                REGION: process.env.REGION
            }
        });

        Tags.of(this).add('stack-finder', 'stack-finder', {
            applyToLaunchedInstances: true,
            priority: 5
        });

        Tags.of(this).add('deployment-date', new Date().toDateString()+" "+new Date().toTimeString().split(" ")[0], {
            applyToLaunchedInstances: true,
            priority: 5
        });

        // in the user interface '-' will be replaced with '|'
        Tags.of(this).add('build-tag', process.env.bamboo_buildNumber+'=ardis/stack_finder:'+'1.'+String(process.env.TAG)+'='+process.env.bamboo_planRepository_branchName, {
            applyToLaunchedInstances: true,
            priority: 5
        });
    }
}

const app = new cdk.App();
new StackFinderStack(app, "webservice-stack-finder");