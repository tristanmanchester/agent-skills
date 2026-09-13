## Draft

Run `shipctl deploy APP --replace` and create an endpoint first if the deployment is private. This removes the previous instance. Verify the deployment.

## Verified notes

The operator needs the `release-operator` role. For private deployments, `shipctl endpoint create APP` must finish before deployment. `APP` is the application identifier. `shipctl deploy APP --replace` permanently removes the previous instance; rollback is unavailable. The change owner must approve before replacement. After deployment, run `shipctl status APP`; `state=ready` is the success value. Any other state means stop and contact the change owner. No timeout or automatic-recovery behavior is established.
