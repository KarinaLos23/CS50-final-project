function uploadPhoto() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = "image/png,image/jpeg"
    input.onchange = e => {
        var file = e.target.files[0];
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = readerEvent => {
            var content = readerEvent.target.result; // this is the content!
            jQuery.ajax({
                url: "/upload_photo",
                type: "POST",
                async: false,
                data: JSON.stringify(content),
                contentType: 'application/json'
            })
            document.getElementById("profile_pic").src = readerEvent.target.result;
        }
    }
    input.click();


}