#!/usr/bin/env python3
"""
   Copyright 2023 NetApp, Inc

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys

import astraSDK


def exec(args, ard):
    if args.objectType == "app":
        rc = astraSDK.apps.unmanageApp(quiet=args.quiet, verbose=args.verbose).main(args.appID)
        if rc is False:
            print("astraSDK.apps.unmanageApp() failed")
            sys.exit(1)
    elif args.objectType == "bucket":
        rc = astraSDK.buckets.unmanageBucket(quiet=args.quiet, verbose=args.verbose).main(
            args.bucketID
        )
        if rc is False:
            print("astraSDK.buckets.unmanageBucket() failed")
            sys.exit(1)
    elif args.objectType == "cluster":
        rc = astraSDK.clusters.unmanageCluster(quiet=args.quiet, verbose=args.verbose).main(
            args.clusterID
        )
        if rc:
            # "Private" cloud clusters+credentials also should be deleted
            if ard.needsattr("clusters"):
                ard.clusters = astraSDK.clusters.getClusters().main()
            for cluster in ard.clusters["items"]:
                for label in cluster["metadata"]["labels"]:
                    if (
                        cluster["id"] == args.clusterID
                        and label["name"] == "astra.netapp.io/labels/read-only/cloudName"
                        and label["value"] == "private"
                    ):
                        if astraSDK.clusters.deleteCluster(
                            quiet=args.quiet, verbose=args.verbose
                        ).main(args.clusterID, cluster["cloudID"]):
                            if astraSDK.credentials.destroyCredential(
                                quiet=args.quiet, verbose=args.verbose
                            ).main(cluster.get("credentialID")):
                                print(f"Credential deleted")
                            else:
                                print("astraSDK.credentials.destroyCredential() failed")
                                sys.exit(1)
                        else:
                            print("astraSDK.clusters.deleteCluster() failed")
                            sys.exit(1)
        else:
            print("astraSDK.clusters.unmanageCluster() failed")
            sys.exit(1)
    elif args.objectType == "cloud":
        if ard.needsattr("cloud"):
            ard.clouds = astraSDK.clouds.getClouds().main()
        rc = astraSDK.clouds.unmanageCloud(quiet=args.quiet, verbose=args.verbose).main(
            args.cloudID
        )
        if rc:
            # Cloud credentials also should be deleted
            for cloud in ard.clouds["items"]:
                if cloud["id"] == args.cloudID:
                    if cloud.get("credentialID"):
                        if astraSDK.credentials.destroyCredential(
                            quiet=args.quiet, verbose=args.verbose
                        ).main(cloud.get("credentialID")):
                            print(f"Credential deleted")
                        else:
                            print("astraSDK.credentials.destroyCredential() failed")
                            sys.exit(1)
        else:
            print("astraSDK.clusters.unmanageCloud() failed")
            sys.exit(1)
