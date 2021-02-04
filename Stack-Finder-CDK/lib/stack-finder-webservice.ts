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
            vpcId: 'vpc-',
            availabilityZones: ['us-west-2a', 'us-west-2b'],
            privateSubnetIds: ['subnet-', 'subnet-'],
            publicSubnetIds: ['subnet-', 'subnet-'],
            publicSubnetRouteTableIds: ['rtb-', 'rtb-'],
            privateSubnetRouteTableIds: ['rtb-', 'rtb-']
        });

        const dc_web_access_sg = ec2.SecurityGroup.fromSecurityGroupId(this, 'security-group-stack-finder', 'sg-');

        const role = Role.fromRoleArn(this, 'TaskRoleArn', 'arn:aws:iam::012345678901:role/ecsTaskExecutionRole', {
            mutable: false
        });

        
       const lb = elb2.ApplicationLoadBalancer.fromApplicationLoadBalancerAttributes(
            this, 'load-balancer-stack-finder', {
                securityGroupId: 'sg-',
                loadBalancerArn: 'arn:aws:elasticloadbalancing:us-west-2:012345678901:loadbalancer/app/elb-',
                loadBalancerDnsName: '.us-west-2.elb.amazonaws.com'
            }
        );

        const cluster = ecs.Cluster.fromClusterAttributes(this, 'cluster-stack-finder', {
            clusterName: 'default-cluster',
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
                listenerArn: 'arn:aws:elasticloadbalancing:us-west-2:012345678901:listener/app/elb-',
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
                hostHeader: 'domain.com',
                pathPattern: '/stacks*',
                targetGroups: [healthTarget]
            }
        );

        

        var url = "https://ardis-dev.pnl.gov/stacks";
        new CfnOutput(this, "BambooLink", {exportName: "BambooLink", value: "https://your.domain.com/bamboo/browse/"+String(process.env.bamboo_planKey)});
        new CfnOutput(this, 'LoadBalancerDNS', { value: lb.loadBalancerDnsName });
        new CfnOutput(this, 'MessageEndpoint', { exportName: 'message-endpoint-stack-finder', value:  url });
        new CfnOutput(this, 'webServiceName', { exportName: 'webservice-name-stack-finder', value: webService.serviceName });
        new CfnOutput(this, 'webClusterArn', { exportName: 'web-cluster-arn-stack-finder', value: cluster.clusterArn });
        new CfnOutput(this, 'LogGroup', { exportName: 'log-group-stack-finder', value: '/ecs/stack-finder'});
    }
}