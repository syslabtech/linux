To give a user **read-only access** to security roles and users in Kibana, you'll need to configure permissions using **Kibana's role-based access control** features. Specifically, you need to create (or modify) a role in Kibana with permissions to view the **Security** features, but restrict them to **read-only** access.

Here are the steps to accomplish this:

### Step 1: Create a New Role in Kibana
1. Go to **Kibana** > **Stack Management** > **Roles**.
2. Click **Create role**.

### Step 2: Configure Role Permissions
1. **Kibana Privileges**: 
   - Under the **Kibana** section, specify the **Kibana space** you want the user to access (such as `default` if you want this to apply across all spaces).
   - Grant the **Read** privilege for **Stack Management**. This will allow the user to view configuration pages in Stack Management, including **Users and Roles**.

2. **Cluster Privileges**:
   - Under **Elasticsearch privileges** > **Cluster privileges**, add:
     - `manage_security`: Allows viewing security-related configuration, such as roles and users.
     - `manage_api_key` (optional, only if the user needs to view API keys).
     - `read_ilm`, if you also want them to view index lifecycle management.

   > Note: While `manage_security` generally provides access to view users and roles, **it’s not fine-grained to support purely read-only** permissions. Users with this permission will have broader visibility but not necessarily the ability to make changes unless given additional privileges.

3. **Index Privileges**:
   - This step is optional unless the user also needs read-only access to specific indices.
   - If needed, define index-level permissions to restrict access to specific indices, assigning them **read** privileges on the desired indices.

### Step 3: Assign the Role to a User
1. After creating the role, go to **Stack Management** > **Users**.
2. Find the user you want to give read access to, or create a new user if needed.
3. Assign the newly created **read-only security role** to the user.

### Step 4: Test the Access
1. Log in as the user with the new role to verify that they can:
   - Access **Stack Management**.
   - View **Users** and **Roles** in the **Security** section.
   - Cannot make any modifications.

### Summary of Required Permissions
- **Kibana privileges**: Read access to **Stack Management** in the relevant Kibana space.
- **Cluster privileges**: `manage_security` (necessary for viewing users and roles)
