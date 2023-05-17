import uuid
import time
from ..logging import log

from .. import connectors
from ..message import Message
from .. import db
from .. import robots


def streaming_notify(msg, error_msg=None):
    if error_msg:
        msg.msgtype = 'error'
        msg.content = error_msg
    if msg.streaming:
        msg.event.set()


async def process(msg: Message):
    error_msg = None

    # Route
    route = await db.channel_routes.get_route(msg.connector, msg.connector_id)
    if not route:
        error_msg = "Channal not found, drop the message. connector=%s, connector_id=%s" % (
            msg.connector, msg.connector_id)
        log.error(error_msg)
        streaming_notify(msg, error_msg)
        return

    channel = await db.channels.get(route.channel_id)
    if not channel:
        error_msg = "Channel not found, channel_id=%s" % route.channel_id
        log.error(error_msg)
        streaming_notify(msg, error_msg)
        return
    msg.channel_id = route.channel_id

    # Robot
    robot = None
    if channel.robot_id:
        msg.robot_id = channel.robot_id
        try:
            robot = await robots.get_robot(msg.robot_id)
        except Exception as e:
            error_msg = "Create Robot instance failed: %s" % (str)
            log.error(error_msg, exc_info=e)

    # Reply message
    reply = None

    # Robot generate
    robot_generated = None

    if robot:
        try:
            robot_generated = await robot.generate(msg)
        except Exception as e:
            # log.error("Robot generate failed:", exc_info=e)
            error_msg = "Robot generate failed: %s" % str(e)

        reply = msg.copy()
        reply.robot_id = channel.robot_id
        reply.id = uuid.uuid1().hex
        reply.direction = 1
        reply.send_time = int(time.time())
        reply.created_time = reply.send_time

        if robot_generated:
            reply.content = robot_generated
        else:
            reply.content = error_msg

    # Save recevied message to database
    await db.messages.save(**msg.dict())

    # Save and send reply message
    if reply:
        # Save reply to database
        await db.messages.save(**reply.dict())

        # Send to connector
        if not msg.streaming:
            await connectors.manager.send(reply)

    # Make sure that the streaming event is properly notified
    streaming_notify(msg, error_msg)
