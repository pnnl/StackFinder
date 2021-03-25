import { Construct, CfnOutput, Duration } from '@aws-cdk/core';
import { Repository } from '@aws-cdk/aws-ecr';
import { Role } from '@aws-cdk/aws-iam';
import ecs = require('@aws-cdk/aws-ecs');
import ec2 = require('@aws-cdk/aws-ec2');
import elb2 = require('@aws-cdk/aws-elasticloadbalancingv2');
import { LogGroup } from '@aws-cdk/aws-logs';


export interface WebServiceProps {
    repository: string,
    tag: string,
    container_env: {},
    memoryLimitMiB: number,
    cpu: number,
}

export class WebService extends Construct {
    constructor(scope: Construct, id: string, props: WebServiceProps) {
        super(scope, id);

        const repository = Repository.fromRepositoryName(this, 'repository-stack-finder', props.repository);

        const vpc = ec2.Vpc.fromVpcAttributes(this, 'vpc-stack-finder', {
            vpcId: 'vpc-0f94c45582fddf8d3',
            availabilityZones: ['us-west-2a', 'us-west-2b'],
            privateSubnetIds: ['subnet-03566bf4fb38625cf', 'subnet-0a78040a961aa7479'],
            publicSubnetIds: ['subnet-0f0e8eaf4df836b78', 'subnet-02a1099a610ac9ef3'],
            publicSubnetRouteTableIds: ['rtb-08ca0aa7e8e0e3b15', 'rtb-0707ce68c98d44cdc'],
            privateSubnetRouteTableIds: ['rtb-064b11fc98c0a6e12', 'rtb-03ade6ab8a2de13c7']
        });

        const dc_web_access_sg = ec2.SecurityGroup.fromSecurityGroupId(this, 'security-group-stack-finder', 'sg-07ef0188e13238cb5');

        const role = Role.fromRoleArn(this, 'TaskRoleArn', 'arn:aws:iam::026180904564:role/ecsTaskExecutionRole', {
            mutable: false
        });

        
       const lb = elb2.ApplicationLoadBalancer.fromApplicationLoadBalancerAttributes(
            this, 'load-balancer-stack-finder', {
                securityGroupId: 'sg-07ef0188e13238cb5',
                loadBalancerArn: 'arn:aws:elasticloadbalancing:us-west-2:026180904564:loadbalancer/app/elb-ardis-dc-n25-dev/4ecdb540b435f460',
                loadBalancerDnsName: 'internal-elb-ardis-dc-n25-dev-1898410798.us-west-2.elb.amazonaws.com'
            }
        );

        const cluster = ecs.Cluster.fromClusterAttributes(this, 'cluster-stack-finder', {
            clusterName: 'ardis-n25-dc',
            vpc,
            securityGroups: [dc_web_access_sg]
        });

        const webTask = new ecs.FargateTaskDefinition(this, 'task-def-stack-finder', {
            memoryLimitMiB: props.memoryLimitMiB,
            family: 'stack-finder',
            cpu: props.cpu,
            executionRole: role,
            taskRole: role,
        });

        const container = webTask.addContainer('webcontainer-stack-finder', {
            image: ecs.ContainerImage.fromEcrRepository(repository, props.tag),
            environment: props.container_env,
            logging: new ecs.AwsLogDriver({ 
                streamPrefix: 'ecs',
                logGroup: LogGroup.fromLogGroupName(this, 'loggroup-stack-finder', '/ecs/stack-finder')
            })
        });

        container.addPortMappings({
            containerPort: 8080,
            hostPort: 8080,
            protocol: ecs.Protocol.TCP
        });

        const webService = new ecs.FargateService(this, 'service-stack-finder', {
            cluster: cluster,
            desiredCount: 1,
            taskDefinition: webTask,
            assignPublicIp: true,
            securityGroup: dc_web_access_sg,
            serviceName: 'stack-finder-webservice'
        });

        const listen = elb2.ApplicationListener.fromApplicationListenerAttributes(
            this, 'application-listener-stack-finder', {
                listenerArn: 'arn:aws:elasticloadbalancing:us-west-2:026180904564:listener/app/elb-ardis-dc-n25-dev/4ecdb540b435f460/fe37cd8c5d8f2df3',
                securityGroup: dc_web_access_sg
            }
        );


        const healthTarget = new elb2.ApplicationTargetGroup(
            this, 'health-target-group-stack-finder', {
                port: 8080,
                healthCheck: {
                    path: '/stacks/health',
                },
                targets: [webService],
                vpc: vpc,
                targetGroupName: "stack-finder-target-group"
            }
        );
        
        listen.addTargetGroups(
            'targetGroups-stack-finder', {
                priority: 1600,
                hostHeader: 'ardis-dev.pnl.gov',
                pathPattern: '/stacks*',
                targetGroups: [healthTarget]
            }
        );

        

        var url = "https://ardis-dev.pnl.gov/stacks";
        new CfnOutput(this, "BambooLink", {exportName: "BambooLink", value: "https://ci.pnnl.gov/bamboo/browse/"+String(process.env.bamboo_planKey)});
        new CfnOutput(this, 'LoadBalancerDNS', { value: lb.loadBalancerDnsName });
        new CfnOutput(this, 'MessageEndpoint', { exportName: 'message-endpoint-stack-finder', value:  url });
        new CfnOutput(this, 'webServiceName', { exportName: 'webservice-name-stack-finder', value: webService.serviceName });
        new CfnOutput(this, 'webClusterArn', { exportName: 'web-cluster-arn-stack-finder', value: cluster.clusterArn });
        new CfnOutput(this, 'LogGroup', { exportName: 'log-group-stack-finder', value: '/ecs/stack-finder'});
    }
}