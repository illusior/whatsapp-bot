#!/bin/bash

msg1="Farewell :)"
msg2="Everything is loaded and shines, see you space cowboy..."
Goodbyes() {
    echo
    echo $1
    exit
}

echo
echo "looking for ninjas installed"
(echo -n "nginx found at location: " && command -v nginx) ||
(echo "nginx not found. downloading" && sudo apt install nginx)

echo
echo "looking for python installed"
base_python_interpreter=`which python3`
([[ $base_python_interpreter != "" ]] && echo -n "python found at location: $base_python_interpreter") ||
(echo "python not found. downloading" && sudo apt install python3)

# common
project_path=`pwd`
env_name=""
project_name=${PWD##*/}                # to assign to a variable
project_name=${project_name:-/}        # to correct for the case where PWD=/

# nginx config
port=""
project_domain=""

echo
read -p "Your domain without protocol exactly like in settings.py (for example: google.com): " project_domain
read -p "Your port (for example: 80): " port
read -p "Environment name folder to create (for example: env): " env_name
echo
echo "We are assuming your project in $project_path/src folder"
echo "There must be wsgi.py and settings.py in /src/config folder"

`$base_python_interpreter -m venv $env_name`
source $env_name/bin/activate

download_packages () {
    echo
    echo "downloading project packages"
    echo
    pip install -U pip
    pip install -r requirements.txt
}

echo
echo "Do you wish to install python packages in virtual environment ($env_name)?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) download_packages; break;;
        No ) break;;
    esac
done

echo
echo "Building server settings from templates in server/complete_settings folder"
mkdir -p server/complete_settings
# nginx
sed    -e "s~%domain%~$project_domain~g" \
       -e "s~%port%~$port~g" \
       -e "s~%work_dir%~$project_path~g" \
       -e "s~%project_name%~$project_name~g" \
       server/nginx/site.conf > tmp && mv tmp server/complete_settings/$project_name.conf

# gunicorn
gunicorn_service_name="gunicorn.$project_name.service"
gunicorn_socket_name="gunicorn.$project_name.socket"
gunicorn_service_path="$project_path/server/complete_settings/$gunicorn_service_name"
gunicorn_socket_path="$project_path/server/complete_settings/$gunicorn_socket_name"

sed    -e "s~%venv_dir%~$project_path\/$env_name~g" \
       -e "s~%work_dir%~$project_path~g" \
       -e "s~%project_name%~$project_name~g" \
       server/gunicorn/gunicorn.service > tmp && mv tmp $gunicorn_service_path       

sed    -e "s~%project_name%~$project_name~g" \
       server/gunicorn/gunicorn.socket > tmp && mv tmp $gunicorn_socket_path


enable_gunicorn() {

echo
echo "Enabling gunicorn service and socket"

sudo systemctl daemon-reload
sudo systemctl disable $gunicorn_service_name 2> /dev/null     # remove links from systemd/system/
sudo systemctl stop $gunicorn_service_name 2> /dev/null        # remove socket from run/
sudo systemctl disable $gunicorn_socket_name 2> /dev/null
sudo systemctl stop $gunicorn_socket_name 2> /dev/null
sudo systemctl -q enable $gunicorn_socket_path && \
    echo "Successfully created symlinks for gunicorn socket"
sudo systemctl start $gunicorn_socket_name 2> /dev/null #idk why error | journalctl -u $gunicorn_socket_name
sudo systemctl -q enable $gunicorn_service_path && \
    echo "Successfully created symlinks for gunicorn service"
sudo systemctl start $gunicorn_service_name

}

disable_gunicorn() {
    sudo systemctl disable $gunicorn_service_name 2> /dev/null
    sudo systemctl stop $gunicorn_service_name 2> /dev/null        # remove socket from run/
    sudo systemctl disable $gunicorn_socket_name 2> /dev/null
    sudo systemctl stop $gunicorn_socket_name 2> /dev/null
    echo
    echo "Successfully disabled gunicorn service and socket"
}

echo
echo "Do you wish to turn on gunicorn or disable it?"
is_gunicorn_disabled=false
select yn in "On" "Off"; do
    case $yn in
        On ) 
            enable_gunicorn
            break;;
        Off ) 
            disable_gunicorn
            is_gunicorn_disabled=true
            break;;
    esac
done

if [[ $is_gunicorn_disabled == true ]]; then
    echo
    echo "Do you wish to turn off nginx?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) 
                sudo systemctl stop nginx;
                Goodbyes $msg1;;
            No ) 
                Goodbyes $msg1;;
        esac
    done
fi


# nginx boot
echo
echo "Checking nginx configuration file"
sudo nginx -t

if [[ $? == 0 ]]; then
    sudo systemctl is-active nginx > /dev/null
    if [[ $? == 0 ]]; then
        echo
        echo "Do you wish to restart nginx?"
        select yn in "Yes" "No"; do
            case $yn in
                "Yes" )
                    sudo systemctl restart nginx; 
                    break;;
                "No" ) 
                    break;;
            esac
        done
    else
        echo
        echo "nginx is not running. Booting"
        sudo systemctl start nginx;
    fi
    echo
    echo "Creating nginx symlinks"
    sudo ln -sf $project_path/server/complete_settings/$project_name.conf /etc/nginx/sites-enabled/
    sudo ln -sf $project_path/server/complete_settings/$project_name.conf /etc/nginx/sites-available/

    echo
    echo "Reallow ufw rules: $port and 'Nginx Full'"
    sudo ufw allow 'Nginx Full'
    sudo ufw allow $port
    Goodbyes "$msg2"
else
    echo
    echo "Wrong nginx configuration. Exit"
    Goodbyes $msg1
fi





