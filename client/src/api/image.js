import http from '@/utils/http'

export function getVisualize(url) {
    return http({
        url: `/api/analyse/visualize`,
        method: 'GET',
        data: {
            url: url
        },
        responseType: 'blob',
        headers: {
            'Content-Type': 'multipart/form-data' // 设置请求头
        }
    })
}

export function test(text) {
    return http({
        url: `/api/analyse/text`,
        method: 'POST',
        data: {
            text: text
        },
        headers: {
            'Content-Type': 'multipart/form-data' // 设置请求头
        }
    })
}

export function getImage(image_id) {
    return request({
        url: `/api/getimg/${image_id}`,
        method: 'GET',
        responseType: 'blob',
    })
}