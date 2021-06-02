'use strict';

function getCookie(name)
{
    let cookieValue = null;
    if (document.cookie && document.cookie !== '')
    {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++)
        {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '='))
            {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initCamera()
{
    if (navigator.mediaDevices.getUserMedia)
    {
        return navigator.mediaDevices.getUserMedia({audio: false, video: true})
        .then(function (stream)
        {
            document.querySelector('video').srcObject = stream;
            return RecordRTC(stream,
            {
                type: 'video',
            });
        })
        .catch(function (e)
        {
            console.log("Camera get error", e);
        });
    }
    else
    {
        alert('Failed');
    }
}

async function record(streamRecorder, url)
{
    document.querySelector('button').disabled = true
    streamRecorder.startRecording();
    const sleep = m => new Promise(r => setTimeout(r, m));
    await sleep(500);

    streamRecorder.stopRecording(function ()
    {
        let blob = streamRecorder.getBlob();
        upload(blob, url);
    });
}

function upload(blob, url)
{
    let file = new File([blob], 'msr-' + (new Date).toISOString().replace(/:|\./g, '-') + '.webm',
        {
            type: 'video/webm'
        });

    let formData = new FormData();
    formData.append('video-name', file.name);
    formData.append('video-blob', file);

    makeXMLHttpRequest(url, formData, function (request)
    {
        console.log('File uploaded');
        alert(request.responseText);
        window.location.reload();
    })
}

function makeXMLHttpRequest(url, data, callback)
{
    let request = new XMLHttpRequest();
    request.onreadystatechange = function()
    {
        if (request.readyState === 4) callback(request);
    };
    request.onloadstart
    request.open('POST', url);
    request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    request.send(data);
}
