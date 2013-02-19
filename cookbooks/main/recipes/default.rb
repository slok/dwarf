
# Update repos
if platform?("ubuntu")
    include_recipe "apt"
    execute "Update apt repos" do
        command "apt-get update"
    end
end

# Install all dependencies
include_recipe 'build-essential'
include_recipe 'python'
include_recipe 'rabbitmq'
include_recipe 'sudo'

# ----------Setup Python stuff-------------
USER = "vagrant"

sudo 'requirements' do
  user      USER
  runas     'root'
  commands  ['pip install -r /vagrant/requirements.txt']
end
